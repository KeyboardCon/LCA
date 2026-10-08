# BC1 electric kettle: TianGong archive screening

## 1. Study identity and purpose

Run ID: `baseline-archive-20261008`. Study date: 2026-10-08 (Korea). Goal:
assess the factory-gate climate-change impact of one packaged 1 L electric
kettle and document where data are insufficient. Student alias: unknown.
Repository: `https://github.com/KeyboardCon/LCA`. Intended class comparison:
GWP100 per packaged kettle. This is an **incomplete screening run**, not a
comparable final result. There is no independent complete-result Git tag,
revised run, or final submission SHA.

## 2. Product, unit and boundary

Declared unit: one packaged BC1 simple plastic 1 L electric kettle at the
factory gate. The classroom PDF attributes its bill of materials to the
*EU Electric Kettles preparatory study* (2020), Task 4, Tables 4-3, 4-4 and
4-8. The transcribed [BOM](data/bom.csv) is 723 g kettle plus 137.8 g
packaging, or 860.8 g total. The intended boundary includes raw materials,
component manufacture, assembly and packaging. Customer delivery, use and
end of life are excluded. The archival background processes are mainly CN;
the actual kettle production location and reference year are unknown.

## 3. Foreground inventory and assumptions

All 12 finished masses are sourced from the classroom PDF and entered in the
BOM. The model assumes that a selected resin or metal process makes the
finished mass at 100% yield **only for scaling its recorded direct exchanges**;
actual material purchase requirements are unknown. Material grades, forming
losses, injection molding, metal forming, film extrusion, assembly electricity,
transport and scrap treatment are not supplied. Their burdens are **missing**, 
not zero. No prices or monetary proxies are used. The script converts grams to
kilograms and divides by each process's reference output in kilograms.
Potential manufacturing burdens already included in each process have not
been independently verified; no separate conversion service is added.

## 4. Data and matching

Background source: archived `tiangong-lca/data` release `0.2.0`, Git commit
`c50cab7961e0b0ca11c26a600bd4c90fea6c6c32`. Its README states that
maintenance and GitHub release downloads ended on 2026-06-21; current data
are available from the TianGong platform. The
[match table](data/matches.csv) and [search log](data/search_log.md) give
queries, alternatives and decisions. The [result manifest](results/baseline.json)
contains dataset names, UUIDs, versions, years, locations, reference flow
UUIDs/amounts, source URLs, hashes and unresolved flow links. Files were
retrieved 2026-10-08. Seven material matches are provisional and five are
unmatched. These are unit-process inventories, **not cumulative cradle-to-gate
factors**. Several records explicitly lack upstream energy or feedstock data.

## 5. Calculation and impact method

[`assess.py`](assess.py) reads the local ILCD XML. For each provisionally
matched material, it scales the process to its finished mass, sums recorded
direct elementary output flows, and multiplies flow UUIDs by matching
characterization factors. The method is the archive's Environmental Footprint
`Climate change` GWP100, UUID `6209b35f-9447-40b5-b68c-a1099e3674a0`.
The method XML describes an IPCC 2021 baseline and also references an older
source; the exact published EF version needs verification. Unit-process
upstream suppliers are **not solved** (`As=f` has not been assembled), so the
output is only characterized direct emissions. Product-flow inputs are listed
as unresolved. Allocation and system model follow each source process as
recorded; cross-process consistency is unverified. Recycling credits are not
applied. Biogenic carbon treatment follows only any matching archive factors;
missing flows are not assigned zero. No uncertainty distribution is fitted.

## 6. Reproduce

Requires Python 3 standard library and the checked-out historical data
repository at `/workspace/tiangong-data` (or pass its `tiangong_lca_data`
directory explicitly). No account or API key is needed for this archived
checkout. The official TianGong CLI is checked out at
`/workspace/tiangong-cli` for later current-data retrieval; live use requires
browser OAuth and network access to TianGong Production.

```bash
cd /workspace/LCA
python -m unittest -v test_assess.py
python assess.py --dataset /workspace/tiangong-data/tiangong_lca_data \
  --output results/baseline.json
```

The JSON file can be opened in any editor. The source XML is referenced by
commit and hash; it is not copied into this coursework repository. For a new
machine, clone `https://github.com/tiangong-lca/data.git` and check out
`c50cab7961e0b0ca11c26a600bd4c90fea6c6c32` before running.

## 7. Results, checks and interpretation

**Full GWP100: not calculated.** The JSON contains `null` for the total,
because five materials, manufacturing operations and upstream suppliers are
unresolved. The characterized direct-emission **subtotal of selected unit
processes** is `0.0331150182 kg CO2-eq` per packaged kettle, of which
`0.033054450` is from the selected copper process and `0.0000605682` from
the selected LDPE process. The other selected process records have no matched
GWP-emission exchanges in this calculation; their full burdens are unknown.
This subtotal cannot be interpreted as the kettle footprint or a lower bound.
There are no defensible top-three contributors to the complete product.

Checks: BOM mass and reference units pass. The direct subtotal equals the sum
of recorded direct contributions. Supplier closure fails, and the full
double-counting check cannot pass without conversion-service data. The result
is most affected by missing upstream material production and forming, not by
numerical precision. CN historical processes are imperfect proxies for an
unspecified kettle production region and year.

## 8. Uncertainty and sensitivity

Not calculated because the baseline is incomplete. No probability ranges,
Monte Carlo draws, seed, or P05/P95 are reported. Alternate steel, copper,
PP, PVC and cardboard process choices are recorded in the search log for a
future scenario; they are not presented as a revised numerical result.

## 9. Codex and human decisions

Codex prepared the project on 2026-10-08 using the model displayed in this
chat; exact model build/settings are unavailable. The user selected the
webpage's kettle task and TianGong as the database, then supplied the page as
a PDF and pointed to the TianGong GitHub organization. Codex selected the
provisional process matches, retained missing values, and implemented the
checks. The user has not yet reviewed or accepted the matches. The
[prompt and decision log](PROMPTS.md) records consequential requests and
choices; the [search log](data/search_log.md) records process alternatives.
Private messages and credentials are not included.

## 10. Independent and revised runs

An independent **complete** result has not been produced, committed, tagged,
or compared with classmates. A revision requires a defensible complete
baseline, a preserved original commit, one changed choice, and a second
calculation. None is claimed here.
