# Frontend Error Handling (Detailed Reference)

This page provides the extended version of the frontend error handling & resilience concept. A condensed summary lives inside `frontend.md`.

## 1. Database Access Layer Resilience
**Problem:** Unhandled exceptions from SQL queries caused page crashes.
**Solution:** `commit_select` / `commit_select_scalar` return `[]` on failure (error is logged). Callers use simple falsy checks.
**Impact:** No propagation of transient DB errors into UI; consistent iterable type.

## 2. Database Health Monitoring
`is_db_healthy()` performs a lightweight `SELECT 1`. Distinguishes:
- DB unreachable -> explicit error panel
- DB reachable but empty -> empty state (not an error)

## 3. Unified Error Panels
Reusable `render_error_panel(title, details)` ensures consistent styling for connectivity, data absence, and subsystem failures.

## 4. Time Series & Staleness Robustness
- UTC normalization for timestamps
- Absolute time difference to absorb small clock skew
- Guard empty DataFrames before min/max
- Exception wrapper around history fetch prevents cascading failures

## 5. External API Resilience
Weather API failures yield informational user feedback instead of stack traces; downstream logic checks for `None` gracefully.

## 6. Toast & Feedback Strategy
- Toast only after successful real data load (has at least one non-None value)
- Per-session & per-room flags to avoid spam
- Distinguish load success from mere page render

## 7. Severity Color Coding
| Severity | Component | Usage Examples |
|----------|----------|----------------|
| Red (`st.error`) | Hard failures | DB unreachable, fatal query errors |
| Yellow (`st.warning`) | Degradation | Stale sensor data (>5m) |
| Blue (`st.info`) | Informative transient | Weather API unavailable, staleness check skipped |
| Green (`st.toast`) | Success | Data load completed |

## 8. Rationale
Color & fallback hierarchy reduces alarm fatigue: treat true outages distinctly, while soft failures (external APIs) remain unobtrusive. Empty data is common early in deployments and must not be conflated with infrastructure faults.

## 9. Testing Coverage Snapshot
- Selection helpers: success + simulated exception (empty list fallback)
- Staleness helpers: fresh vs stale vs missing data
- DataFetcher: partial sensor availability & empty states
- History widget: empty dataset & exception guard

## 10. Future Enhancements
- Metrics endpoint exporting health counters & last error timestamps
- Differentiation: "No data yet" vs. "Filtered range has no rows"
- Incremental circuit breaker for repeated DB failures (progressive backoff)
- Optional Sentry/OpenTelemetry integration for richer diagnostics
- Configurable toggle: return `None` vs `[]` for error signaling in advanced use-cases

## 11. Design Principles
1. Fail soft, not silent (log errors, show user-friendly panel)
2. Preserve UX continuity over strict error purity
3. Make severity visually scannable
4. Prefer idempotent, side-effect free health probes
5. Keep caller contracts simple (iterables not `Optional[Iterable]`)

## 12. Quick Reference (Cheat Sheet)
| Aspect | Mechanism | Location |
|--------|-----------|----------|
| DB health | `is_db_healthy()` | `database/sql/engine.py` |
| Safe selection | empty list fallback | `database/sql/engine.py` |
| Error panel | `render_error_panel` | `frontend/utils.py` |
| Staleness check | absolute delta <= 5 min | `utility/currentness.py` |
| History safety | try/except + DataFrame guards | `generic_analytics/widgets/history_widget.py` |
| Weather resilience | info message on failure | `generic_analytics/widgets/utils.py` |
| Toast gating | session state flags | `overview.py`, `generic_analytics.py` |
