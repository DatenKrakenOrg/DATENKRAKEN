# 3. Dokumentation der Optimierungen

Dieses Kapitel belegt drei durchgeführte Optimierungen mit Ziel, Maßnahme, Umsetzung und (soweit möglich) messbarem Effekt im Vergleich zum vorherigen Zustand.

Optimierungen im Scope:
1. Aktualisierung & Prozess für Mock-Daten
2. Vereinheitlichtes Deployment via `docker-compose.yml`
3. Frontend Error Handling & Resilience Layer

## 3.1 Mock-Daten Aktualisierung
Das bestehende SQL Skript `database/utils/fill_dummy.sql` wurde aktualisiert (Felder/Zeiträume), aber es existiert weiterhin kein automatisierter Generator, kein Schema-Diff Check und keine Parametrisierung.

| Aspekt | Vorher (veraltet) | Jetzt (Ist) | Ziel (geplant / empfohlen) | Nutzen bei Erreichen |
|--------|-------------------|------------|----------------------------|---------------------|
| Skript Aktualität | Veraltet | Aktualisiert | Laufende Drift-Prüfung | Verlässliche Testbasis |
| Generierungsprozess | Manuell | Manuell | Parametrisierter Generator | Reproduzierbarkeit |
| Qualitätssicherung | Keine | Keine | Automatisierter Schema-Diff | Frühe Drift-Erkennung |
| Datenrealismus | Zufall | Zufall | Muster (Tag/Nacht, Peaks) | Validere UI/Performance Tests |
| Reproduzierbarkeit | Nein | Nein | Seed-Steuerung | Vergleichbarkeit |
| Datenumfang | Fix 60 Tage | Fix 60 Tage | Konfigurierbar (Tage) | Schnellere lokale Runs |

### Bisherige Maßnahme (tatsächlich erfolgt)
- Aktualisierung des bestehenden SQL Skripts (Generierung 60 Tage historische Zufallsdaten für mehrere Sensoren und Geräte).

### Empfohlene Folgemaßnahmen
- Separater Generator (Python) + Schema-Diff.
- Parametrisierung (Dauer, Anzahl Geräte, Musterprofile).
- CI Drift-Check.

### Metrik-Vorschläge (noch nicht implementiert)
| Metrik | Zielwert | Erhebung (geplant) |
|--------|---------|-------------------|
| Schema-Diff Count | 0 | `schema_compare.py` |
| Dummy-Datensätze pro Sensor | >=24h Abdeckung | Generator-Log |

### Begründung
Realitätsnahe Testdaten reduzieren False Positives bei UI Tests & verbessern Performance-Assessments.

## 3.2 Deployment via Docker Compose
| Aspekt | Vorher | Nachher | Nutzen |
|--------|--------|---------|--------|
| Startkomplexität | Mehrere manuelle Startschritte (DB, MQTT, Services) | Ein Befehl `docker compose up` | Einstieg beschleunigt |
| Umgebungskonsistenz | Unterschiedliche lokale Setups | Einheitliche definierte Dienste | Weniger "Works on my machine" |
| Dokumentation | Zentral | Zentral im Compose + README | Transparenz |
| Skalierung Test | Mühsam | Profile/Overrides möglich | Schnellere Experimente |

### Maßnahme
- Erstellung einer `docker-compose.yml` mit Services: DB (Timescale), MQTT Broker, Subscription Script, Frontend, Monitoring.
- Einheitliche `.env` Variablen pro Service + `example.env`.

### Vorher/Nachher Indikatoren
| Indikator | Vorher (geschätzt) | Nachher (Ziel) |
|-----------|--------------------|----------------|
| Onboarding-Zeit bis erstes Dashboard | 60 Min | <10 Min |
| Manuelle Schritte | >6 | 1 |

### Begründung
Reduziert Prozess-Variabilität und schafft Basis für QA + Produktionsnähe.

## 3.3 Frontend Error Handling & Resilience
Implementiert sind DB Health Check, Safe Selection (Empty List Fallback), Basis Fehlerpanel, Staleness-Check Funktionen. Noch nicht (oder nur teilweise) implementiert: konsistente Info/Warning Differenzierung für alle Pfade, Erfolgstoasts, externe API spezifische Fallbacks, Circuit Breaker.

| Aspekt | Vorher | Ist | Ziel | Nutzen bei Erreichen |
|--------|--------|-----|------|---------------------|
| DB Fehlerbehandlung | Crash / Trace | Fehlerpanel + leere Liste | Ergänzung Retry/Circuit | Höhere Robustheit |
| Fehlerpanel Konsistenz | Ad-hoc / inkonsistent | Basis Panel `render_error_panel` | Einheitliches Severity-Mapping | Klarheit für Nutzer |
| Staleness Transparenz | Keine | Funktionen vorhanden (teilweise genutzt) | Einheitliche Warnanzeige | Erkennbare Datenfrische |
| Externe API Fehler | Ausnahmeanzeige | Keine spezielle Behandlung | Info Panel + Degradation Status | Reduzierte Frustration |
| Erfolgssignal (Toast) | Keins | Nicht vorhanden | Einmaliges Toast bei Erstdaten | Positives Feedback |
| Telemetrie / Observability | Keine | Keine | Sentry / OTel Integration | Schnellere Ursachenanalyse |
| Testabdeckung Fehlerpfade | Gering | Teilweise (Selection Tests) | Voll (Stale, Leer, Offline, API) | Nachweis Resilienz |

### Implementierte Prinzipien (Stand)
- "Fail soft" für DB Zugriffe (Fallback leere Liste)
- Frühe Health-Prüfung statt spät im Widget
- Staleness-Check Funktionen vorhanden

### Noch nicht umgesetzte Prinzipien (aus Zielbild)
- Einheitliche Farb-/Severity-Matrix für alle Pfade
- Erfolgstoasts / differenzierte Soft-Fail Panels
- API-spezifische Resilience Layer

### Metrik-Ideen (Ziel – aktuell nicht gemessen)
| Kennzahl | Vorher | Ziel | Messung (geplant) |
|----------|--------|------|------------------|
| Ungefangene UI Exceptions / 100 Sessions | n/a | <1 | Log Parser / Telemetrie |
| Erst-Daten Erfolgsfeedback | n/a | >90% Sessions mit einmaligem Toast | Session State |
| Fehlertyp-Differenzierung (hart/soft/info) | Keine | Vollständig abgedeckt | Code Review / UI Snapshot |

### Begründung
Verhindert White-Screen Situationen, erhöht Vertrauen & Fehlertoleranz ohne Benutzer zu überfrachten.

## 3.4 Zusammenfassung Wirkung
| Optimierung | Primäre ISO 25010 Attribute | Wirkung (Ist – Qualitativ) | Wirkung (Ziel – Quantifizierbar) |
|-------------|-----------------------------|----------------------------|---------------------------------|
| Mock-Daten | Maintainability (leicht), Functional Suitability | Skript aktualisiert, weiterhin manuell & zufällig | 0 Schema-Diffs / Sprint, parametrisierbar |
| Docker Compose | Portability, Reliability | Einheitliches Startverfahren (falls umgesetzt) | <10 Min Setup Zeit |
| Error Handling | Reliability, Usability | DB Fehler & Staleness teilweise abgefedert | <1 ungefangene Exception / 100 Sessions |

