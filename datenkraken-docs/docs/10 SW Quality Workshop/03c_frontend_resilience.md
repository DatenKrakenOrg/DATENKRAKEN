# Optimization: Frontend Resilience & Error Handling

## Objectives
Provide a user-facing dashboard that fails gracefully, communicates state clearly, and degrades predictably during partial outages.

## Principles
| Principle | Application |
|----------|-------------|
| Fail fast & visibly | Detect backend/mqtt unavailability quickly and show status banners |
| Progressive enhancement | Core data panels render even if advanced widgets fail |
| Observable failures | Structured logging + browser console clarity |
| User guidance | Provide actionable retry / reload suggestions |

## Error classes
| Class | Example | UX Strategy |
|-------|---------|-------------|
| Network timeout | DB query exceeds threshold | Skeleton + retry button |
| MQTT disconnect | Broker unreachable | Banner warning, stale badge |
| Data schema drift | Missing expected field | Soft fallback + log warning |
| Aggregation delay | Gold materialization late | Timestamp indicator + stale label |
| Auth / permission (future) | Unauthorized dashboard area | Redirect + message |

## Patterns Implemented
1. Central fetch wrapper with timeout + error normalization.
2. Stale data indicators (last update timestamp, color coding).
3. Component-level suspense (loading skeletons for charts / tables).
4. Banner system (stackable global alerts: WARN, ERROR, INFO).
5. MQTT connection monitor (state machine: connecting → active → degraded → offline).
6. Graceful degradation path: charts → numeric backups → placeholder.

## Example state model (MQTT)
```
[connecting] --success--> [active]
[connecting] --timeout--> [degraded]
[active] --heartbeat_missing--> [degraded]
[degraded] --reconnect_success--> [active]
[degraded] --timeout--> [offline]
[offline] --manual_retry--> [connecting]
```

## UI Signals
| Signal | Meaning | Location |
|--------|---------|----------|
| Green dot | Live stream | Header status block |
| Amber triangle | Degraded (stale > threshold) | Header + panel footer |
| Red hollow circle | Offline (no updates) | Header + panel overlay |
| Grey clock | Historical render (no live) | Panel footer |

## Logging taxonomy
| Level | Usage |
|-------|------|
| debug | Connection attempts, retries |
| info | Successful reconnect, resubscription |
| warn | Stale data threshold exceeded |
| error | Unhandled fetch failure, JSON parse issue |

## Testing Matrix
| Scenario | Method | Expected |
|----------|--------|----------|
| Broker down at load | Simulate refused TCP | Offline banner + retry |
| Late gold aggregate | Delay materialized view | Stale label appears |
| Random JSON field drop | Modify mock API | Fallback path triggered + warn log |
| Flaky reconnect | Inject intermittent failures | State oscillates degraded/active |

## Future Enhancements
- Client-side circuit breaker for failing endpoints
- Telemetry export (OpenTelemetry browser spans)
- Offline caching (IndexedDB) for last-known values
- Role-based feature flags (hide sensitive panels)

## KPIs
| KPI | Target |
|-----|--------|
| Time to visible error (network) | < 2s |
| False positive stale warnings | < 3% |
| Successful auto-reconnect ratio | > 90% |
| User forced refresh frequency | < 1 per hour |
