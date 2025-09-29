# Documentation of Implemented Optimizations

This chapter evidences three implemented optimizations: objectives, actions, current state, and (where feasible) qualitative / potential quantitative impact vs. the previous state.

Optimizations in scope:
1. Update & process clarification for mock data
2. Unified deployment via single `docker-compose.yml`
3. Frontend error handling & resilience layer

## Mock Data Update
The existing SQL script `database/utils/fill_dummy.sql` was updated (fields / periods) but still: no automated generator, no schema diff check, no parameterization.

| Aspect | Before (outdated) | Now (current) | Target (planned / recommended) | Value if achieved |
|--------|------------------|--------------|-------------------------------|-------------------|
| Script freshness | Outdated | Updated | Continuous drift check | Reliable test basis |
| Generation process | Manual | Manual | Parameterized generator | Reproducibility |
| Quality assurance | None | None | Automated schema diff | Early drift detection |
| Data realism | Random | Random | Patterns (day/night, peaks) | More valid UI/perf tests |
| Reproducibility | No | No | Seed control | Comparability |
| Data volume | Fixed 60 days | Fixed 60 days | Configurable (days) | Faster local runs |

### Implemented action (actually done)
- Update of existing SQL script (generates 60 days random historical data for multiple sensors/devices).

### Recommended follow-ups
- Separate Python generator + schema diff.
- Parameterization (duration, device count, pattern profiles).
- CI drift check.

### Metric ideas (not implemented)
| Metric | Target | Planned capture |
|--------|--------|-----------------|
| Schema diff count | 0 | `schema_compare.py` |
| Dummy rows per sensor | ≥24h coverage | Generator log |

### Rationale
More realistic data lowers false positives in UI tests & improves performance assessments.

## Deployment via Docker Compose
| Aspect | Before | After | Benefit |
|--------|--------|-------|---------|
| Startup complexity | Multiple manual steps (DB, MQTT, services) | Single `docker compose up` | Faster onboarding |
| Environment consistency | Divergent local setups | Unified defined services | Fewer “works on my machine” cases |
| Documentation | Scattered | Central in compose + README | Transparency |
| Scaling tests | Cumbersome | Profiles / overrides feasible | Faster experiments |

### Action
- Created unified `docker-compose.yml` (TimescaleDB, MQTT broker, subscription script, frontend, monitoring (optional)).
- Standardized `.env` variables + `example.env`.

### Before / After indicators
| Indicator | Before (estimate) | After (target) |
|-----------|-------------------|---------------|
| Onboarding time to first dashboard | 60 min | <10 min |
| Manual steps | >6 | 1 |

### Rationale
Reduces process variability; baseline for QA & production likeness.

## Frontend Error Handling & Resilience
Implemented: DB health check, safe selection (empty list fallback), basic error panel, staleness checking functions. Not (or only partially) implemented: consistent info/warning differentiation across all paths, success toasts, external API specific fallbacks, circuit breaker.

| Aspect | Before | Current | Target | Value if achieved |
|--------|--------|---------|--------|------------------|
| DB error handling | Crash / trace | Error panel + empty list | Add retry / circuit | Higher robustness |
| Error panel consistency | Ad-hoc / inconsistent | Basic panel `render_error_panel` | Unified severity mapping | User clarity |
| Staleness transparency | None | Functions exist (partially used) | Unified warning display | Freshness awareness |
| External API errors | Raw exception | No specific handling | Info panel + degradation status | Reduced frustration |
| Success signal (toast) | None | Not present | One-time toast on first data | Positive feedback |
| Telemetry / observability | None | None | Sentry / OTel integration | Faster root cause analysis |
| Test coverage error paths | Low | Partial (selection tests) | Full (stale, empty, offline, API) | Resilience evidence |

### Implemented principles
- “Fail soft” for DB access (empty list fallback)
- Early health check before deep UI rendering
- Staleness check helpers present

### Not yet implemented (target principles)
- Unified color / severity matrix across all flows
- Success toasts / differentiated soft‑fail panels
- API specific resilience layer

### Metric ideas (target – not currently measured)
| Metric | Before | Target | Measurement (planned) |
|--------|--------|--------|-----------------------|
| Uncaught UI exceptions / 100 sessions | n/a | <1 | Log parser / telemetry |
| First-data success feedback | n/a | >90% sessions once | Session state |
| Error type differentiation (hard/soft/info) | None | Fully covered | Code review / UI snapshot |

### Rationale
Prevents white-screen situations; increases trust & resilience without overwhelming users.

## Impact summary
| Optimization | Primary ISO 25010 attributes | Current (qualitative) | Target (quantifiable) |
|-------------|------------------------------|-----------------------|-----------------------|
| Mock data | Maintainability (minor), Functional suitability | Script updated, still manual & random | 0 schema diffs / sprint, parameterizable |
| Docker compose | Portability, Reliability | Unified startup (if adopted) | <10 min setup time |
| Error handling | Reliability, Usability | DB failures & staleness partially cushioned | <1 uncaught exception / 100 sessions |
