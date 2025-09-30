# Optimization: Unified Deployment (Docker Compose)

## Initial situation
Deployment required multiple separate compose files / invocations (DB, frontend, subscription script, MQTT). Consequences:
- High cognitive load (ordering / dependencies)
- Inconsistent environment variable configuration
- Higher error risk (forgotten flags / services)
- Longer onboarding for new developers

## Goals
| Goal | Description | KPI |
|------|------------|-----|
| One-command start | Entire system via one command | `docker compose up` |
| Unified env management | Shared `.env` / service `example.env` | Complete documentation |
| Health transparency | Basic healthchecks integrated | All core containers `healthy` |
| Faster onboarding | Reduced time to functioning dashboard | <10 min |

## Target architecture (services)
| Service | Role | Key dependencies |
|---------|------|------------------|
| timescaledb | Sensor / aggregate persistence | Data volume, network |
| mqtt-broker | Message transport | Port 1883 |
| subscription | Consumes MQTT → writes DB | Depends on MQTT + DB |
| frontend | Dashboard / UI | DB (read), optional monitoring |
| monitoring (optional) | Uptime / metrics | DB reachability |

## Actions
1. Merge distributed compose files → single root file.
2. Conventions: network aliases `db`, `mqtt`.
3. Healthchecks for DB & optional frontend HTTP.
4. Unified env variable naming (`DB_HOST`, `MQTT_HOST`).
5. Document start/stop/logs in README.
6. Optional overrides for dev mounts / hot reload.

## Before / After comparison
| Criterion | Before | After |
|----------|--------|-------|
| Startup steps | >6 manual commands | 1 (compose up) |
| Ordering errors (DB not ready) | Frequent | Minimized |
| Documentation overhead | High | Reduced |
| New dev onboarding | 45–60 min | <10 min |

## Risks & mitigation
| Risk | Description | Mitigation |
|------|------------|-----------|
| Over‑compose (monolith) | Harder differentiated deployments | Optional profiles / flags |
| Image version drift | Uncoordinated tag updates | Renovate / Dependabot |
| Credential leaks | `.env` accidentally committed | `.gitignore` + example file |

## Extensions (future)
- Prod-specific compose (readonly volumes, stricter networks)
- Prometheus / Grafana integration
- Reverse proxy (nginx/traefik) for TLS / routing

## KPIs (post implementation)
| KPI | Target | Measurement |
|-----|--------|-------------|
| Onboarding time | <10 min | Self report + timer |
| Failed start rate (first 3 attempts) | <10% | Onboarding log |
| Healthcheck success rate | >99% local start | Compose logs |
