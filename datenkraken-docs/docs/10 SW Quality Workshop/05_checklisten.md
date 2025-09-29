# (Legacy Filename) Slim Quality Checklist & Minimal Definition of Done

> NOTE: This file kept temporarily only to avoid broken references during the filename migration. Primary maintained version: `05_slim_checklist.md`. Will be removed after link integrity verification.

This chapter provides only submission-relevant verification points.

## Analysis coverage
| Item | Goal | Status |
|------|------|--------|
| Current state & weakness analysis present | `01_current_state_weaknesses.md` | OK |
| Extended SFMEA incl. new failure modes | `02_extended_sfmea.md` (FA13–FA15) | OK |
| Prioritization & rationale for 3 optimizations | `03_optimizations_overview.md` | OK |
| New feature specified (alerting) | `04_alerting_feature.md` (current vs. target) | OK |

## Optimization 1: Mock data
| Evidence | Criterion | Status |
|----------|-----------|--------|
| `03a_mock_data.md` | Clear current vs. target | OK |
| `fill_dummy.sql` updated | Matches current schema | OK |
| No overclaiming | Future items marked | OK |

## Optimization 2: Deployment / compose
| Evidence | Criterion | Status |
|----------|-----------|--------|
| `03b_unified_deployment.md` | Unified approach described | OK |
| Example `.env` present | Reproducible | OK |
| Alerting env variables documented | Threshold & SMTP clear | OK |

## Optimization 3: Frontend error handling
| Evidence | Criterion | Status |
|----------|-----------|--------|
| `03c_frontend_resilience.md` | Implemented vs. open separated | OK |
| Code fallbacks (empty results) | `engine.py` / `utils.py` | OK |
| Staleness function documented | `currentness.py` referenced | OK |

## New feature: Alerting (Arduino offline)
| Evidence | Criterion | Status |
|----------|-----------|--------|
| Current implementation described | Inactivity + sequence email | OK |
| Target separation | Persistence & UI marked future | OK |
| SFMEA impact explained | RPN table updated | OK |
| Env variables used in code | `alerting.py` / `main.py` | OK |

## Integrity & traceability
| Item | Goal | Status |
|------|------|--------|
| No unsupported implementation claims | Docs match code | OK |
| Future clearly labeled | No mixing | OK |
| All new files dated | Placeholders removed | OK |

## Minimal Definition of Done (for this submission)
A contribution (doc/code) is done when:
1. Relevant document updated or created (see 5.1–5.5).
2. No false “current state” claims (only verified code referenced).
3. Future elements clearly labeled ("Future", "Target", "Not implemented").
4. Env/config dependencies documented (if applicable).
5. Cross references (filenames) accurate.

## Open improvement potential (not submission relevant)
- Automated tests for sequence gaps & offline simulation
- Schema diff script / latency measurement
- Persistent alerting state machine & UI badges
- Extended accessibility verification