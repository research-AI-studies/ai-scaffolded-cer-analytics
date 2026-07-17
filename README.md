

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21408917.svg)](https://doi.org/10.5281/zenodo.21408917)

This repository contains the **code-only, public** artifacts for the InquiTrace
research program: the inquiry-platform design, the CER-aligned instrumentation
schema, a hybrid (LLM + rule-based) scaffolding-agent specification, and a fully
reproducible learning-analytics pipeline.

## Scope and honesty statement
This repository supports a **methods + systems** contribution and a
**pre-registered protocol** for a future classroom study. It does **not** report
empirical classroom findings. All numbers produced here come from a clearly
labelled, non-real **example cohort** and exist only to demonstrate that the
pipeline runs end-to-end. Real classroom data, once collected, will be placed in
`data/private/` (git-ignored) and analysed by the identical pipeline.

## Repository layout
```
ai-scaffolded-cer-analytics/
├── generate_example.py       # produces the public example cohort
├── src/
│   ├── analyze.py            # pipeline orchestrator -> outputs/results.json
│   ├── agent_policy.py       # deterministic fallback scaffolding policy
│   ├── clustering.py         # engagement clustering
│   ├── sequence_analysis.py  # trajectory / transition analysis
│   ├── qa_coding.py          # Q&A coding scheme
│   ├── make_figures.py       # figures (offline)
│   └── make_tables.py        # tables (offline)
├── data/
│   ├── example/              # PUBLIC illustrative cohort (not real)
│   └── private/              # OFFLINE real data (git-ignored; empty here)
├── docs/schema_crosswalk.md  # stage->CER and data-model crosswalk
├── tests/                    # pytest suite
├── outputs/results.json      # single source of truth (generated; git-ignored)
└── .gitignore
```

## Reproduce the demonstration
```bash
pip install pandas scipy
python generate_example.py     # writes data/example/*.csv
python src/analyze.py          # writes outputs/results.json
```

## What is defensible vs. deferred
- **Defensible now (this paper):** platform architecture, CER-to-stage mapping,
  scaffolding taxonomy + fallback decision algorithm, the analytics pipeline,
  and the pre-registered analysis plan and hypotheses.
- **Deferred to the future study:** any empirical claim about how AI scaffolding
  affects children's CER reasoning, effect sizes, and significance tests.

## Data availability
The example cohort is included for reproducibility. No real or processed pupil
data is distributed. A versioned snapshot of this public code is archived on
Zenodo (cite the concept DOI).

## Citation
Please cite the **concept DOI**, which always resolves to the latest version:

> https://doi.org/10.5281/zenodo.21408917

Machine-readable metadata is in `CITATION.cff`.
