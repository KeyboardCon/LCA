"""Auditable, deliberately incomplete kettle screening using archived ILCD data."""

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
DEFAULT_DATASET = HERE.parent / "tiangong-data" / "tiangong_lca_data"
PROCESS = "{http://lca.jrc.it/ILCD/Process}"
FLOW = "{http://lca.jrc.it/ILCD/Flow}"
FLOW_PROPERTY = "{http://lca.jrc.it/ILCD/FlowProperty}"
UNIT_GROUP = "{http://lca.jrc.it/ILCD/UnitGroup}"
METHOD = "{http://lca.jrc.it/ILCD/LCIAMethod}"
COMMON = "{http://lca.jrc.it/ILCD/Common}"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
MASS_PROPERTY = "93a60a56-a3c8-11da-a746-0800200b9a66"
GWP_METHOD = "6209b35f-9447-40b5-b68c-a1099e3674a0"
ARCHIVE_COMMIT = "c50cab7961e0b0ca11c26a600bd4c90fea6c6c32"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def english_name(root, path):
    for item in root.findall(path):
        if item.get(XML_LANG) == "en":
            return item.text or ""
    return ""


def flow_description(reference):
    return english_name(reference, f"{COMMON}shortDescription") or reference.findtext(f"{COMMON}shortDescription") or "unknown"


def flow_type_and_property(dataset, flow_id):
    path = dataset / "flows" / f"{flow_id}.xml"
    if not path.is_file():
        return None, None
    root = ET.parse(path).getroot()
    kind = root.findtext(f".//{FLOW}typeOfDataSet")
    reference_id = root.findtext(f".//{FLOW}referenceToReferenceFlowProperty")
    property_id = None
    for prop in root.findall(f".//{FLOW}flowProperty"):
        if prop.get("dataSetInternalID") == reference_id:
            ref = prop.find(f"{FLOW}referenceToFlowPropertyDataSet")
            property_id = ref.get("refObjectId") if ref is not None else None
    return kind, property_id


def validate_mass_unit(dataset):
    property_root = ET.parse(dataset / "flowproperties" / f"{MASS_PROPERTY}.xml").getroot()
    unit_ref = property_root.find(f".//{FLOW_PROPERTY}referenceToReferenceUnitGroup")
    if unit_ref is None:
        raise ValueError("Mass property has no unit group")
    group_id = unit_ref.get("refObjectId")
    group = ET.parse(dataset / "unitgroups" / f"{group_id}.xml").getroot()
    reference_id = group.findtext(f".//{UNIT_GROUP}referenceToReferenceUnit")
    for unit in group.findall(f".//{UNIT_GROUP}unit"):
        if unit.get("dataSetInternalID") == reference_id:
            if unit.findtext(f"{UNIT_GROUP}name") == "kg" and Decimal(unit.findtext(f"{UNIT_GROUP}meanValue")) == 1:
                return
    raise ValueError("Mass property reference unit is not kg")


def validate_dataset_commit(dataset):
    result = subprocess.run(["git", "-C", str(dataset.parent), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True)
    if result.stdout.strip() != ARCHIVE_COMMIT:
        raise ValueError("Archive checkout is not the pinned TianGong data commit")
    status = subprocess.run(["git", "-C", str(dataset.parent), "status", "--porcelain",
                             "--untracked-files=normal", "--", "tiangong_lca_data"],
                            capture_output=True, text=True, check=True)
    if status.stdout.strip():
        raise ValueError("Archived TianGong data files are modified or untracked")


def factors(dataset):
    path = dataset / "lciamethods" / f"{GWP_METHOD}.xml"
    root = ET.parse(path).getroot()
    result = {}
    for factor in root.findall(f".//{METHOD}factor"):
        ref = factor.find(f"{METHOD}referenceToFlowDataSet")
        value = factor.findtext(f"{METHOD}meanValue")
        direction = factor.findtext(f"{METHOD}exchangeDirection")
        if ref is not None and value is not None and direction == "Output":
            key = ref.get("refObjectId")
            if key in result and result[key] != Decimal(value):
                raise ValueError(f"Conflicting GWP factor for {key}")
            result[key] = Decimal(value)
    version = root.findtext(f".//{COMMON}dataSetVersion")
    return result, sha256(path), version


def assess(dataset):
    validate_dataset_commit(dataset)
    validate_mass_unit(dataset)
    bom = read_csv(HERE / "data" / "bom.csv")
    matches = {row["material"]: row for row in read_csv(HERE / "data" / "matches.csv")}
    if len(matches) != len(bom) or {row["material"] for row in bom} != set(matches):
        raise ValueError("BOM and match table do not have the same unique materials")
    totals = defaultdict(Decimal)
    for row in bom:
        mass = Decimal(row["mass_g"])
        if mass <= 0:
            raise ValueError("BOM masses must be positive")
        totals[row["part"]] += mass
    if totals != {"Kettle": Decimal("723"), "Packaging": Decimal("137.8")}:
        raise ValueError(f"BOM does not match the classroom mass check: {dict(totals)}")

    cf, method_hash, method_version = factors(dataset)
    results = []
    subtotal = Decimal(0)
    cache = {}
    for row in bom:
        material = row["material"]
        mapping = matches[material]
        entry = {"material": material, "part": row["part"], "mass_g": row["mass_g"],
                 "match_status": mapping["status"], "match_rationale": mapping["rationale"],
                 "process_uuid": mapping["process_uuid"] or None,
                 "characterized_direct_gwp100_kg_co2e": None}
        if not mapping["process_uuid"]:
            results.append(entry)
            continue
        path = dataset / "processes" / (mapping["process_uuid"] + ".xml")
        root = ET.parse(path).getroot()
        ref_id = root.findtext(f".//{PROCESS}referenceToReferenceFlow")
        name = english_name(root, f".//{PROCESS}dataSetInformation/{PROCESS}name/{PROCESS}baseName")
        use_advice = english_name(root, f".//{PROCESS}useAdviceForDataSet")
        dataset_type = root.findtext(f".//{PROCESS}typeOfDataSet")
        allocation_approach = root.findtext(f".//{PROCESS}LCIMethodApproach")
        broken_sources = [ref.get("refObjectId") for ref in root.findall(f".//{PROCESS}referenceToDataSource")
                          if "#REF!" in (ref.get("refObjectId") or "") or "#REF!" in (ref.get("uri") or "")]
        version = root.findtext(f".//{COMMON}dataSetVersion")
        year = root.findtext(f".//{COMMON}referenceYear")
        location = root.find(f".//{PROCESS}locationOfOperationSupplyOrProduction")
        reference = None
        exchanges = []
        for exchange in root.findall(f".//{PROCESS}exchange"):
            flow_ref = exchange.find(f"{PROCESS}referenceToFlowDataSet")
            if flow_ref is None:
                raise ValueError(f"Exchange without flow in {path}")
            amount_text = exchange.findtext(f"{PROCESS}meanAmount")
            if amount_text is None:
                raise ValueError(f"Exchange without amount in {path}")
            record = (flow_ref.get("refObjectId"), exchange.findtext(f"{PROCESS}exchangeDirection"),
                      Decimal(amount_text), flow_description(flow_ref))
            exchanges.append(record)
            if exchange.get("dataSetInternalID") == ref_id:
                reference = record
        if reference is None or reference[1] != "Output" or reference[2] <= 0:
            raise ValueError(f"Invalid reference flow in {path}")
        if reference[0] not in cache:
            cache[reference[0]] = flow_type_and_property(dataset, reference[0])
        if cache[reference[0]] != ("Product flow", MASS_PROPERTY):
            raise ValueError(f"Reference flow is not a kg-mass product flow in {path}")
        scale = Decimal(row["mass_g"]) / Decimal(1000) / reference[2]
        direct = Decimal(0)
        uncharacterized = []
        upstream = {}
        missing_flow_definitions = []
        nonreference_outputs = []
        for flow_id, direction, amount, flow_name in exchanges:
            if amount == 0 or flow_id == reference[0]:
                continue
            if flow_id not in cache:
                cache[flow_id] = flow_type_and_property(dataset, flow_id)
            kind, property_id = cache[flow_id]
            if kind is None:
                missing_flow_definitions.append({"flow_uuid": flow_id, "flow_name": flow_name,
                                                 "direction": direction, "source_mean_amount": str(amount),
                                                 "source_unit": "unknown: flow XML absent"})
            elif kind == "Elementary flow" and direction == "Output":
                if flow_id in cf and property_id == MASS_PROPERTY:
                    direct += amount * scale * cf[flow_id]
                else:
                    uncharacterized.append(flow_id)
            elif kind == "Product flow" and direction == "Input":
                upstream[flow_id] = {"flow_uuid": flow_id, "flow_name": flow_name,
                                     "provider_process_uuid": None}
            elif kind == "Product flow" and direction == "Output":
                nonreference_outputs.append({"flow_uuid": flow_id, "flow_name": flow_name,
                                             "source_mean_amount": str(amount),
                                             "source_unit": "kg" if property_id == MASS_PROPERTY else "not verified"})
        entry.update({"process_name": name, "process_version": version,
                      "process_year": year,
                      "process_dataset_type": dataset_type,
                      "process_use_advice": use_advice,
                      "process_allocation_approach": allocation_approach,
                      "broken_source_reference_ids": broken_sources,
                      "process_location": location.get("location") if location is not None else None,
                      "process_source_url": "https://github.com/tiangong-lca/data/blob/c50cab7961e0b0ca11c26a600bd4c90fea6c6c32/tiangong_lca_data/processes/" + mapping["process_uuid"] + ".xml",
                      "process_file_sha256": sha256(path),
                      "reference_flow_uuid": reference[0], "reference_amount_kg": str(reference[2]),
                      "reference_unit": "kg",
                      "process_scale": str(scale),
                      "characterized_direct_gwp100_kg_co2e": str(direct),
                      "unresolved_upstream_input_flow_uuids": sorted(upstream),
                      "unresolved_upstream_inputs": [upstream[key] for key in sorted(upstream)],
                      "missing_flow_definitions": missing_flow_definitions,
                      "nonreference_product_outputs": nonreference_outputs,
                      "uncharacterized_direct_output_flow_uuids": sorted(set(uncharacterized))})
        subtotal += direct
        results.append(entry)
    return {"study": "BC1 packaged 1 L electric kettle at factory gate",
            "boundary": "Materials, component manufacture, assembly, packaging; excludes delivery, use, end of life",
            "dataset": "Archived TianGong LCA data 0.2.0; current platform data not retrieved",
            "archive_commit": ARCHIVE_COMMIT,
            "retrieval_date": datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat(),
            "method": "Environmental Footprint Climate change GWP100; archived method UUID " + GWP_METHOD,
            "method_version": method_version,
            "method_source_url": "https://github.com/tiangong-lca/data/blob/c50cab7961e0b0ca11c26a600bd4c90fea6c6c32/tiangong_lca_data/lciamethods/" + GWP_METHOD + ".xml",
            "method_file_sha256": method_hash,
            "bom_mass_g": {key: str(value) for key, value in totals.items()},
            "total_finished_mass_g": str(sum(totals.values())),
            "materials": results,
            "selected_materials": sum(bool(x["process_uuid"]) for x in results),
            "unmatched_materials": sum(not x["process_uuid"] for x in results),
            "characterized_direct_emission_subtotal_kg_co2e": str(subtotal),
            "gwp100_total_kg_co2e": None,
            "calculation_status": "incomplete diagnostic: provisional matches, missing materials, upstream suppliers, allocation and manufacturing operations",
            "checks": {"bom_mass_balance": "passed: 723 g kettle + 137.8 g packaging = 860.8 g",
                       "reference_units": "passed for selected reference product flows: mass in kg; not a full exchange-unit audit",
                       "contribution_sum": "passed for characterized direct-emission subtotal only",
                       "supplier_closure": "failed: unresolved product inputs and absent manufacturing steps",
                       "flow_definitions": "incomplete: some process exchanges reference absent flow XML files",
                       "allocation": "not assessed: copper source declares market-value allocation and also outputs slag; allocation factor not verified",
                       "double_counting": "not fully assessed: carton process includes cutting/printing; future conversion steps need overlap review"},
            "warning": "The unallocated characterized direct-emission diagnostic is NOT the kettle footprint or a lower bound; missing contributions are unknown, not zero."}


def write_mapping_csv(result, path):
    fields = ["material", "mass_g", "database", "release", "dataset_name",
              "dataset_uuid", "dataset_version", "geography", "year",
              "reference_flow_uuid", "reference_amount_kg", "reference_unit",
              "source_url", "retrieval_date", "file_sha256", "match_status",
              "match_rationale", "unresolved_upstream_input_count",
              "uncharacterized_direct_output_flow_uuid_count", "missing_flow_definition_exchange_count",
              "nonreference_product_output_exchange_count", "source_dataset_type",
              "source_allocation_approach", "broken_source_reference_count", "source_use_advice"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item in result["materials"]:
            writer.writerow({
                "material": item["material"], "mass_g": item["mass_g"],
                "database": "TianGong LCA historical archive",
                "release": "0.2.0; commit " + result["archive_commit"],
                "dataset_name": item.get("process_name", "unknown"),
                "dataset_uuid": item.get("process_uuid") or "unknown",
                "dataset_version": item.get("process_version", "unknown"),
                "geography": item.get("process_location", "unknown"),
                "year": item.get("process_year", "unknown"),
                "reference_flow_uuid": item.get("reference_flow_uuid", "unknown"),
                "reference_amount_kg": item.get("reference_amount_kg", "unknown"),
                "reference_unit": item.get("reference_unit", "unknown"),
                "source_url": item.get("process_source_url", "unknown"),
                "retrieval_date": result["retrieval_date"],
                "file_sha256": item.get("process_file_sha256", "unknown"),
                "match_status": item["match_status"],
                "match_rationale": item["match_rationale"],
                "unresolved_upstream_input_count": len(item.get("unresolved_upstream_input_flow_uuids", [])),
                "uncharacterized_direct_output_flow_uuid_count": len(item.get("uncharacterized_direct_output_flow_uuids", [])),
                "missing_flow_definition_exchange_count": len(item.get("missing_flow_definitions", [])),
                "nonreference_product_output_exchange_count": len(item.get("nonreference_product_outputs", [])),
                "source_dataset_type": item.get("process_dataset_type", "unknown"),
                "source_allocation_approach": item.get("process_allocation_approach", "unknown"),
                "broken_source_reference_count": len(item.get("broken_source_reference_ids", [])),
                "source_use_advice": item.get("process_use_advice", "unknown"),
            })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=HERE / "results" / "baseline.json")
    parser.add_argument("--mapping-output", type=Path, default=HERE / "results" / "mapping.csv")
    args = parser.parse_args()
    result = assess(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_mapping_csv(result, args.mapping_output)
    print(f"Saved {args.output} and {args.mapping_output}; status: {result['calculation_status']}")


if __name__ == "__main__":
    main()
