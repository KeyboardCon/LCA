# Curated Codex prompt and decision log

Date: 2026-10-08 (Asia/Seoul). Assistant: Codex (GPT-6; exact model build and
runtime settings unavailable). This is a paraphrased record of consequential
requests and decisions, not a verbatim private conversation. No credentials,
contact details or private account data are included.

| Step | User request or correction (paraphrased) | Decision and evidence | Outcome |
| --- | --- | --- | --- |
| 1 | Determine whether the uploaded `cli-main.zip` is an LCA database. | Inspected its package metadata, CLI executable and `tidas-schemas` JSON. Those files define software and data formats; the small CSV is an import test. | Identified the ZIP as a CLI source repository, not process inventory data. |
| 2 | Set up TianGong access and do the kettle LCA work. | Read the official CLI instructions. Cloned `tiangong-lca/cli`, installed its pinned Node/pnpm dependencies and built it. Browser OAuth is required for current Production records. | CLI build passed and 26 relevant tests passed. Current live records were not retrieved. |
| 3 | Use the kettle shown on the course page. | The live course site returned proxy HTTP 403. The user supplied a six-page PDF capture; its finished-mass BOM and factory-gate boundary were transcribed into `data/bom.csv`. | Mass check: 723 g kettle + 137.8 g packaging = 860.8 g. |
| 4 | Try TianGong's GitHub organization as the data source. | Found and cloned the official `tiangong-lca/data` repository at commit `c50cab7961e0b0ca11c26a600bd4c90fea6c6c32`. Its README says the archive stopped being maintained in June 2026. | Used archived process XML and an archived GWP100 method; did not represent it as current TianGong Production data. |
| 5 | Assess the environmental impact using TianGong data. | Searched English process names, inspected reference outputs, exchanges and method factors. Selected seven provisional process matches, left five materials unmatched, and recorded alternatives in `data/search_log.md`. | Implemented an auditable direct-emission calculation. Full supplier closure and manufacturing inventory remain unavailable, so full GWP100 is `null`. |
| 6 | Make the Python files visible on GitHub. | Verified the local tests and staged only the code, derived BOM/mapping, README and result manifest. Used the repository alias for commit attribution. | Pushed the incomplete screening project to `KeyboardCon/LCA` on `main`. |
| 7 | Organize the consequential prompts. | Added this curated log and linked it from the README. | Decisions and limitations can be reviewed without publishing the chat transcript. |
| 8 | Check README against every field in the classroom PDF and update GitHub. | Audited all ten sections; added a parameter/status table, source and method details, portable reproduction commands, explicit missing checks and preserved screening commit. Updated the calculation manifest with method version and reference units, then reran tests. | The README describes the incomplete status more precisely; no full footprint was invented. |
| 9 | Recheck the README against the supplied `readme-requirements.md` and update GitHub. | Confirmed the ten required sections, generated an input-level mapping CSV, identified unknown specifications and alias, documented access permissions and uncertainty limits, and retested reproduction. | README and artifacts were updated without presenting a missing total as zero. |
| 10 | Re-read the entire six-page PDF, check for omissions and provide the final commit SHA. | A separate PDF audit and technical audit checked the README against all pages and recalculated the two nonzero direct terms. They found that carton conversion was partly included, copper has a slag output and unverified allocation, and some flow XML files are missing. The code now reports these gaps, verifies a clean pinned data checkout, and the README limits its claims. | This is still a diagnostic screening, not a full kettle GWP100 result. The final SHA is supplied separately after the GitHub commit. |

## Match decisions and unresolved work

- Accepted **provisionally**: electric-furnace stainless steel, copper-zinc
  alloy as brass, primary refined copper, gas-phase PP, ethylene-route PVC,
  LDPE resin, and corrugated carton. The grade, process route, location and
  forming steps are not confirmed for the actual kettle.
- Rejected as unsupported for the baseline: Nylon 6/66 fiber processes as a
  substitute for unspecified kettle nylon, and arbitrary resin proxies for
  POM, PC, ABS or silicone. No monetary proxy was introduced.
- The finished BOM masses were used to scale the provisional processes. No
  measured manufacturing loss, assembly electricity, transport, scrap or
  recycled-content assumption was supplied; these are unresolved, not zero.
- The archived process output `0.0331150182 kg CO2-eq` is a characterized
  direct-emission diagnostic. Copper attribution is unverified because the
  source also outputs slag and declares market-value allocation. It is **not**
  the kettle's full climate impact.
- Current TianGong Production access still needs the saved network-policy
  change to be published and a human browser OAuth login. Any current-data
  replacement should record its own dataset IDs, versions, retrieval dates,
  mapping decisions and an independent result before class comparison.
