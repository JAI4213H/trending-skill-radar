# Flaw coverage matrix

| Original shortcoming | Countermeasure | Implementation / test | Remaining limitation |
|---|---|---|---|
| Undefined discovery process | Explicit workflow and source policy | `SKILL.md`, `source_policy.md` | Live connector orchestration is external |
| News mistaken for skills | Canonical skill IDs and claim separation | `skill_taxonomy.yaml`, `test_pipeline.py` | Classification is rule/input driven |
| Subjective scoring | Versioned weighted dimensions | `radar_core.py`, `test_pipeline.py` | Weights require future validation |
| No historical measurement | Comparable dated activity and zero-baseline guard | `historical_growth`, tests | Sparse real baselines |
| Missing labor evidence | Optional permitted jobs source | `sources.yaml`, `source_policy.md` | No job API bundled |
| Duplicate sources | URL/identifier dedup and origin groups | `deduplicate`, tests | Semantic near-duplicates need review |
| Weak claim verification | IDs, URLs, verification status | `normalize`, report | URL reachability not checked offline |
| Missing uncertainty/coverage | Coverage and confidence labels | `score_skill`, tests | Not statistically calibrated |
| No counterevidence | Counterevidence retained and lowers confidence | `score_skill`, tests | Discovery is caller responsibility |
| No learner prioritization | Separate learning dimension/profile | `score_skill` | Profile schema is intentionally small |
| No backtesting | Evaluation protocol and harness entry point | `evaluation_methodology.md`, tests | Fixture is synthetic |
| No feedback tracking | Evidence IDs and reproducible reports | report output | Outcome tracking not yet implemented |
| Prompt injection | Untrusted-content policy | `security_guidance.md`, `SECURITY.md` | Agents must still follow policy |
| Source failures/rate limits | Source registry and bounded policy | `sources.yaml`, `source_policy.md` | Connectors are optional |
| Missing persistence | Date fields and historical growth | `radar_core.py` | No database included |
| Irreproducible outputs | Methodology version and stable IDs | `radar_core.py`, tests | Clock affects generated date only |
| Trend/value/future conflation | Separate dimensions | scoring docs, report | Inputs need careful extraction |
| Inaccurate confidence | Coverage/source-family thresholds | `confidence`, tests | Heuristic, not calibrated |
| Unsafe scraping | Explicit exclusions | source/security docs | External tools may differ |
| Poor public install docs | README, pyproject, license, CI | repository root | Not published from this checkout |
