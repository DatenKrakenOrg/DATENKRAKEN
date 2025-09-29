# Optimization: Mock Data Update

## Current state (real)
A manually executed SQL script `database/utils/fill_dummy.sql` uses `generate_series` to insert random / synthetic measurements (noise, temperature, humidity, voc) for ~60 days into bronze tables.

History:
- Script was outdated (structure / quantity misaligned) and got updated (fields & distributions aligned).
- NO automated generation or validation (no Python generator, no schema diff) – ad hoc execution only.

Current script scope:
| Table | Generation logic | Frequency | IDs distributed |
|-------|------------------|-----------|-----------------|
| bronze.noise | Random 0–1028 | 1 min (2 offsets) over 60 days | 401/402/403 |
| bronze.temperature | Random 5–30 | Every 30s | Round-robin 401–403 |
| bronze.humidity | Random 5–30 | Every 30s | Round-robin 401–403 |
| bronze.voc | Random 5–30 | Every 30s | Round-robin 401–403 |

Limitations (current):
- No semantic patterns (day/night, peaks, ventilation events)
- No schema verification pre-insert (assumes tables present)
- No parameterization (duration / device count)
- No separation dev vs. test datasets

## Target goals (future – not implemented)
| Goal | Description | Suggested metric |
|------|-------------|------------------|
| Schema conformity | Automatic column/type diff | 0 schema diffs / run |
| Pattern realism | Simulated day/night & outliers | Qualitative review / defined variance |
| Reproducibility | Parameterized generator w/ seed | Fixed seed → same distribution |
| Automation | CI job can generate sample | Successful pipeline run |

## Recommended future actions (not implemented)
1. Python generator (`/tools/mockgen/`) with params: `--rooms`, `--duration-days`, `--pattern day-night|flat`, `--seed`.
2. Schema introspection via `information_schema.columns` → drift warning.
3. Advanced patterns (sinus temperature, CO2 peaks, humidity drift, noise spikes).
4. Validation: type + min/max constraints or abort.
5. Optional nightly CI sample + diff report.

## Risks & mitigation (current vs. recommended)
| Risk | Current state | Mitigation |
|------|--------------|-----------|
| Schema drift | Manual noticing at insert | Automated diff check |
| Unrealistic distribution | Pure random | Patterned generators |
| Non-reproducibility | Every run differs | Seed control |
| Data explosion | Fixed high volume (60 days) | Parametrize duration |

## Extensions (future)
- Sample anonymized production data + hybrid mock
- Statistical distribution checks (KS test vs. reference)
- Outlier injection flags for negative tests

## Evidence (performed change)
| Aspect | Before | Now |
|--------|--------|-----|
| Script freshness | Outdated | Updated (matches current schema) |
| Automation | None | Still none |
| Pattern realism | Simple random | Unchanged |
| Parameterization | None | Unchanged |

## Potential future value
| Goal | Expected benefit |
|------|------------------|
| Validation checks | Early drift detection |
| Realistic patterns | More valid perf & UI tests |
| Reproducibility | Comparable builds |
| Parametrized duration | Faster local datasets |
