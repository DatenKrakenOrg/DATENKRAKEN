# 3c. Optimization: Frontend Error Handling

Important: This optimization targets the frontend only. Backend / ingestion paths did not receive a generalized error handling layer.

## Initial situation
Prior to the layer: database connection issues, empty result sets, external API failures could raise uncaught exceptions → blank or partial pages. Error types were not visually distinguished.

## Goals
| Goal | Description | KPI |
|------|-------------|-----|
| User-friendly degradation | Error states without UI collapse | Zero white screens |
| Differentiated severity | Clear visual escalation | Color / component mapping |
| Minimized alert fatigue | Separate informative vs. critical | Fewer unnecessary `error` panels |
| Testable resilience | Automated coverage for error paths | Tests for empty / stale / exception |

## Component implementation status
| Component | Status | Current description | Reference |
|-----------|--------|---------------------|-----------|
| Safe DB wrapper | Implemented | Returns `[]` on failure (rows / scalars) | `commit_select`, `commit_select_scalar` |
| DB health check | Implemented | Simple `SELECT 1` | `is_db_healthy()` |
| Error panel | Implemented (basic) | Unified error display (only `error`, optional caption) | `render_error_panel` |
| Staleness check | Implemented | Evaluates last measurement age (≤5 min) | `currentness.py` |
| Staleness warning panel | Partial | Boolean available, limited UI integration | `overview.py` usage |
| Info/Warning/Error differentiation | Partial | Basic (error panel + selective st.info/st.warning) | Frontend pages |
| External API handling | Not in scope | No special fallback | — |
| Success toast gating | Not implemented | No one‑time success toast | — |
| Circuit breaker / backoff | Not implemented | Simple failure return only | — |
| Reusable severity mapping table | Target only | No central mapping yet | — |

## Visual severity mapping (target vs. current)
| Status | Target UI component | Current implementation | Note |
|--------|---------------------|------------------------|------|
| Hard failure | `st.error` panel | Present | DB down cases |
| Degradation | `st.warning` | Partial | Staleness context dependent |
| Informational | `st.info` | Sporadic | No consistent pattern |
| Success | `st.toast` | Missing | Could be added for initial load |

## Tests (current vs. target)
| Scenario | Current | Target |
|----------|---------|--------|
| DB offline | Caught by `is_db_healthy()` + panel | Keep |
| Empty table / no values | Sometimes silent (empty list) | Explicit info panel |
| Stale data | Boolean exists, partial UI warning | Consistent warning |
| External API timeout | Not specific | Info panel w/ fallback |
| First successful load | No toast | One-time toast |

## Metric ideas
| Metric | Target | Measurement |
|--------|--------|-------------|
| Uncaught exceptions / 100 sessions | <1 | Log parser |
| White screen session share | 0% | Manual + automated UI tests |
| Error type differentiation implemented | Yes | Code review |
| False negatives (hard failure shown as info) | 0 | Targeted tests |

## Out of scope
- No global observability backend (e.g. Sentry)
- No circuit breaker logic beyond basic fallbacks
- No automated escalation (mail/alert)

## Risks & mitigation
| Risk | Description | Mitigation |
|------|------------|-----------|
| Hidden failure | Empty list masks root cause | Keep logging + explicit panel wording |
| Staleness threshold mis-tuned | Over-sensitive warnings | Adjust constant / config |
| UX overload | Too many panels concurrently | Prioritization (hard > warn > info) |

## Extensions (future)
- Sentry / OpenTelemetry integration
- Circuit breaker after repeated DB failures
- Distinguish “no data ever” vs. “filtered slice empty”

## Evidence of improvement (qualitative – implemented subset)
Before: Uncaught DB failures → unclear UI states / potential crashes.
After: DB failures produce clean error panel; failing selection yields empty lists (UI remains stable). Staleness detection exists, presentation not yet uniform.

## Gaps / next steps
- Consistent `st.info` for “no data yet” instead of silent emptiness
- Optional success toast after first valid dataset
- External API fallback (standard info panel)
- Central severity mapping utility
- Optional telemetry (Sentry / OTel) for uncaught exception measurement
