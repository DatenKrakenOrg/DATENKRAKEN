# 3b. Optimierung: Vereinheitlichtes Deployment (Docker Compose)

## Ausgangslage
Vor der Optimierung bestand der Deployment-Prozess aus mehreren separaten `docker-compose.yml` Dateien / Aufrufen für einzelne Services (z.B. Datenbank, Frontend, Subscription Script, ggf. MQTT). Dadurch:
- Hohe kognitive Last (Reihenfolge / Abhängigkeiten merken)
- Inkonsistente Environment Variablen-Konfiguration
- Erhöhte Fehleranfälligkeit (vergessene Flags / Services)
- Längere Onboarding-Zeit neuer Teammitglieder

## Ziele
| Ziel | Beschreibung | KPI |
|------|--------------|-----|
| One-Command Start | Gesamtsystem mit einem Befehl startbar | `docker compose up` |
| Einheitliche Env-Verwaltung | Gemeinsame `.env` bzw. Service-spezifische `example.env` | Vollständige Dokumentation |
| Health Transparenz | Basis-Healthchecks integriert | `healthy` Status aller Kerncontainer |
| Onboarding Beschleunigung | Reduzierte Zeit bis lauffähiges Dashboard | <10 Min |

## Ziel-Architektur (Services)
| Service | Rolle | Wichtige Abhängigkeiten |
|---------|------|------------------------|
| timescaledb | Persistenz Sensor-/Aggregatdaten | Volume für Daten, Netzwerk |
| mqtt-broker | Nachrichtenvermittlung | Port 1883 |
| subscription | Konsumiert MQTT → schreibt DB | Abhängig von mqtt + db |
| frontend | Dashboard / UI | DB (read), optional Monitoring |
| monitoring (optional) | Uptime / Metrics | DB reachability |

## Maßnahmen
1. Zusammenführen verteilter Compose-Dateien → eine Wurzel-Datei.
2. Konvention: Gemeinsame Netzwerk-Alias: `db`, `mqtt`.
3. Healthchecks für DB & optional HTTP Checks Frontend.
4. Einheitliche Benennung von Env Variablen (`DB_HOST`, `MQTT_HOST`).
5. Dokumentation Start/Stop/Logs im README.
6. Optional: Overrides (`docker-compose.override.yml`) für Entwicklungs-spezifische Mounts / Hot Reload.

## Vorher/Nachher Vergleich
| Kriterium | Vorher | Nachher |
|-----------|--------|---------|
| Startschritte | >6 manuelle Befehle | 1 (Compose Up) |
| Fehler durch fehlende Reihenfolge | Häufig (DB noch nicht bereit) | Minimiert  |
| Dokumentationsbedarf | Hoch | Reduziert |
| Einstieg neuer Dev | 45–60 Min | <10 Min |

## Risiken & Mitigation
| Risiko | Beschreibung | Mitigation |
|--------|--------------|-----------|
| Over-Compose (zu monolithisch) | Schwer differenzierte Deployments | Optionale Profile/Service Flags |
| Versionsdrift Images | Tag Updates unkoordiniert | Renovate / Dependabot Integration |
| Credentials Leaks | .env versehentlich committet | `.gitignore` + `example.env` Vorlage |

## Erweiterungen (Future)
- Prod-spezifische Compose (read-only Volumes, restriktive Netzwerke)
- Integration von Prometheus/Grafana
- Reverse Proxy (nginx/traefik) für TLS / Routing

## KPIs (Erhebung nach Umsetzung)
| KPI | Zielwert | Messung |
|-----|---------|---------|
| Onboarding-Zeit | <10 Min | Selbstbericht + Timer |
| Fehlstart-Rate (erste 3 Versuche) | <10% | Onboarding Protokoll |
| Healthcheck Erfolgsrate | >99% bei lokalem Start | Compose Logs |
