# Archived TianGong match search

Searched English process names in `tiangong-lca/data` commit
`c50cab7961e0b0ca11c26a600bd4c90fea6c6c32` on 2026-10-08.
All selected rows in [matches.csv](matches.csv) are **provisional**. The
archive's `0.2.0` release is historical, and current TianGong platform rows
have not been retrieved.

| BOM input | Search terms | Selected candidate | Other candidate / reason for caution |
| --- | --- | --- | --- |
| Stainless steel | stainless steel | `6fcb8304-d211-4c79-a9de-a1b07058ce02` | Converter route `38c47da1-4683-4beb-8665-6967da3e6b9e`; kettle steel route unknown. Both census records omit energy and feedstock consumption. |
| Brass | brass, copper-zinc alloy | `216385c1-5e30-4122-b31a-afcea87645c0` | Electrolytic-copper route `d58c2083-cf82-402e-8ba1-b14a39d6195a`; composition and forming unknown. |
| Copper | copper production, refined copper | `b70a631e-ea11-4b12-b42c-b0f507a72f6d` | Flash smelting `6d390a38-8a3d-410c-8192-60b70b0bd286`; kettle copper route unknown. Selected source also outputs slag, declares market-value allocation, and has a broken `#REF!` source link. |
| PP | polypropylene | `91a5462f-3a1a-49e9-afec-07b60609dfaf` | Coal-to-PP `b8bcc804-5a15-4a20-8b19-5838f23840e7`; no evidence for that specialized route. Injection molding absent. |
| PVC | polyvinyl chloride | `24fca75a-cefc-483b-8168-e349eb15c25b` | Calcium-carbide route `adb6f36f-9ef7-4b44-b227-dc702350d6a2`; no route information in BOM. |
| Nylon | nylon | none | Archive hits are Nylon 6/66 filament or wire manufacture, while BOM gives no nylon grade or form. |
| POM, PC, ABS, silicone | exact polymer names | none | No defensible polymer-resin production match found from process-name search. |
| LDPE foil | low density polyethylene | `218eaad4-dfc5-4a21-abd3-2e9dd0997fe3` | Resin production only; foil extrusion and losses absent. |
| Cardboard | corrugated carton, cardboard | `b0a8d882-9859-4069-b59b-90dd19dc98a0` | Box-board production `fe1c9c0b-9c65-4ad5-aa4b-a56deabd1987`; actual grade unknown. Selected carton process includes cutting and printing, so do not add those services again without an overlap check. |

Selection is by name and reference product only. It does not prove grade,
technology, location, time, allocation, or upstream completeness. The script
records exact process UUIDs, versions, reference quantities, geography, years,
file hashes and unresolved flow IDs in the result manifest.
