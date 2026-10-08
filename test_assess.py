import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import assess


class AssessmentChecks(unittest.TestCase):
    def test_unpinned_archive_is_rejected(self):
        with patch.object(assess.subprocess, "run", return_value=SimpleNamespace(stdout="wrong-commit\n")):
            with self.assertRaisesRegex(ValueError, "not the pinned"):
                assess.validate_dataset_commit(assess.DEFAULT_DATASET)

    def test_modified_archive_is_rejected(self):
        calls = [SimpleNamespace(stdout=assess.ARCHIVE_COMMIT + "\n"),
                 SimpleNamespace(stdout=" M tiangong_lca_data/processes/example.xml\n")]
        with patch.object(assess.subprocess, "run", side_effect=calls):
            with self.assertRaisesRegex(ValueError, "modified or untracked"):
                assess.validate_dataset_commit(assess.DEFAULT_DATASET)

    def test_archived_method_has_fossil_co2_factor_one(self):
        dataset = assess.DEFAULT_DATASET
        factors, _, _ = assess.factors(dataset)
        self.assertEqual(factors["08a91e70-3ddc-11dd-923d-0050c2490048"], 1)

    def test_missing_mass_fails_before_calculation(self):
        original = assess.read_csv

        def changed(path):
            rows = original(path)
            if path.name == "bom.csv":
                rows[0]["mass_g"] = "185"
            return rows

        with patch.object(assess, "read_csv", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "mass check"):
                assess.assess(assess.DEFAULT_DATASET)

    def test_real_dataset_keeps_incomplete_total_null(self):
        result = assess.assess(assess.DEFAULT_DATASET)
        self.assertIsNone(result["gwp100_total_kg_co2e"])
        self.assertEqual(result["total_finished_mass_g"], "860.80")
        self.assertGreater(result["unmatched_materials"], 0)
        copper = next(x for x in result["materials"] if x["material"] == "Copper")
        self.assertEqual(copper["process_allocation_approach"], "Allocation - market value")
        self.assertTrue(any(x["flow_name"] == "Slag" for x in copper["nonreference_product_outputs"]))
        self.assertEqual(copper["characterized_direct_gwp100_kg_co2e"], "0.033054450")
        ldpe = next(x for x in result["materials"] if x["material"] == "LDPE packaging foil")
        self.assertEqual(ldpe["characterized_direct_gwp100_kg_co2e"], "0.0000605682")
        self.assertEqual(result["characterized_direct_emission_subtotal_kg_co2e"], "0.0331150182")
        polypropylene = next(x for x in result["materials"] if x["material"] == "Polypropylene (PP)")
        self.assertTrue(polypropylene["missing_flow_definitions"])

    def test_mapping_table_preserves_unknown_inputs(self):
        result = assess.assess(assess.DEFAULT_DATASET)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "mapping.csv"
            assess.write_mapping_csv(result, path)
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(row["database"].startswith("TianGong") for row in rows))
        nylon = next(row for row in rows if row["material"].startswith("Nylon"))
        self.assertEqual(nylon["dataset_uuid"], "unknown")
        copper = next(row for row in rows if row["material"] == "Copper")
        self.assertEqual(copper["reference_unit"], "kg")


if __name__ == "__main__":
    unittest.main()
