# InquiTrace Schema Crosswalk

Maps the seven-stage inquiry pipeline to Claim--Evidence--Reasoning (CER)
components and to the logged data model consumed by the analytics pipeline.

## Stage -> CER mapping
| Stage | Activity | CER component | Key logged fields |
|---|---|---|---|
| S0 | Pretest + scenario | Baseline | `quiz_answers[4]` |
| S1 | Soil observation | Evidence (observation) | `observations[soil][dimension]` |
| S2 | Claim formulation | Claim (+ justification) | `claim_text`, `claim_reason` |
| S3 | Stickiness experiment | Evidence (experiment) | `stickiness_rating[soil]`, `fair_test_ok` |
| S4 | Drainage experiment | Evidence (experiment) | `drainage_rate[soil]`, `video_watched` |
| S5 | Evidence organisation | Evidence -> Reasoning | `seeBox`, `thinkBox`, `explain` |
| S6 | Conclusion + post-test | Claim + Reasoning (transfer) | `crop_soil_match[6]`, `posttest[6]` |

## Data model (analytics inputs)
| Table | Grain | Purpose |
|---|---|---|
| `interaction_logs` | event | temporal sequence, help-seeking counts |
| `stage_submissions` | group x stage | CER-component completion quality |
| `agent_decisions` | decision | scaffolding-type + source (LLM vs fallback) |
| `student_qa` | exchange | question-type/function coding |
| `analytics_events` | group | cross-group pattern identification |
| `posttest_errors` | response | misconception categorisation |

## Derived metrics (see `src/analyze.py`)
- Completion rate = completed required fields / required fields (per stage).
- Probe ratio = probe decisions / total agent decisions (per group).
- CER-component completion = groups completing the component / total groups.
- Non-parametric statistics: Spearman rho; Mann-Whitney U (probe strata).

## Agent decision policy
The LLM path is primary; the deterministic fallback (`src/agent_policy.py`) is
used on timeout, schema-validation failure, or off-topic filtering. See that
module for thresholds.
