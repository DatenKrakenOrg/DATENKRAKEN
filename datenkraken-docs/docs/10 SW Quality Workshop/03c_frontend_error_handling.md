# 3c. Optimierung: Frontend Error Handling

Wichtig: Diese Optimierung betrifft ausschließlich das Frontend. Backend-/Ingestion-Pfade wurden nicht mit eigenem generischem Error Handling erweitert.

## Ausgangslage
Vor der Einführung des Error Handling Layers führte eine Reihe von Fehlern (z.B. DB-Verbindungsprobleme, leere Resultsets, externe API-Ausfälle) zu ungefangenen Exceptions und damit teils zu weißen oder unvollständigen Seiten. Fehlertypen waren nicht visuell unterscheidbar.

## Ziele
| Ziel | Beschreibung | KPI |
|------|--------------|-----|
| Benutzerfreundliche Degradation | Fehlerzustände ohne Bruch der UI | Keine White-Screens |
| Differenzierte Severity Stufen | Klare visuelle Eskalation | Farb-/Komponenten-Mapping |
| Minimierte Alarmmüdigkeit | Informative vs. kritische Fehler trennbar | Reduktion unnötiger `error` Panels |
| Testbare Resilienz | Fehlerpfade automatisiert abgedeckt | Tests für: leer, stale, exception |

## Implementierungsstatus der Bausteine
| Baustein | Status | Beschreibung (Ist) | Referenz |
|----------|--------|--------------------|----------|
| Safe DB Wrapper | Implementiert | Rückgabe `[]` bei Fehler (Rows / Scalars) | `commit_select`, `commit_select_scalar` |
| DB Health Check | Implementiert | Einfaches `SELECT 1` | `is_db_healthy()` |
| Fehlerpanel | Implementiert (Basis) | Einheitliche Fehleranzeige (nur `error`, optional caption) | `render_error_panel` |
| Staleness Check | Implementiert | Prüft letzte Messzeit pro Sensor (<=5 Min) | `currentness.py` |
| Warning Panel bei Staleness | Teilweise | Staleness Bool verfügbar, UI-Integration nur auf bestimmten Seiten | `overview.py` Nutzung |
| Differenzierung Info/Warning/Error | Teilweise | Basis vorhanden (error panel + ggf. st.info/st.warning in Pages) | Frontend Pages |
| Externe API Handling | Nicht im Scope | Kein spezieller Fallback implementiert | — |
| Toast Gating (Success Notification) | Nicht implementiert | Kein kontrolliertes einmaliges Success Toast | — |
| Circuit Breaker / Backoff | Nicht implementiert | Nur einfache Fehlerrückgabe | — |
| Wiederverwendbare Severity Mapping Tabelle | Dokumentiert (Ziel) | Noch keine zentrale Mapping-Funktion | — |

## Visual Severity Mapping (Zielbild vs. Ist)
| Status | Ziel UI Komponente | IST Umsetzung | Bemerkung |
|--------|-------------------|---------------|-----------|
| Hard Failure | `st.error` Panel | Vorhanden | DB Down Fälle |
| Degradation | `st.warning` | Teilweise | Staleness Fälle kontextabhängig |
| Informativ | `st.info` | Sporadisch | Noch kein konsistentes Pattern |
| Erfolg | `st.toast` | Nicht vorhanden | Könnte für Erst-Laden ergänzt werden |

## Tests (Aktueller Stand vs. Ziel)
| Szenario | IST | Ziel |
|----------|-----|-----|
| DB offline | Abfang durch `is_db_healthy()` + Panel | Beibehalten |
| Leere Tabelle / keine Werte | Teilweise: leere Listen führen zu neutralem Zustand | Explizites Info Panel |
| Stale Daten | Bool vorhanden, UI teils Warnung | Konsistente Warnanzeige |
| Externe API Timeout | Nicht spezifisch | Info Panel mit Fallback |
| Erstladen Erfolgreich | Kein Toast | Einmaliges Toast |

## Metrik-Ideen
| Kennzahl | Ziel | Messung |
|----------|------|---------|
| Ungefangene Exceptions / 100 Sessions | <1 | Log Parser |
| Anteil White-Screen Sessions | 0% | Manuelles & automatisiertes UI Testing |
| Fehlertyp-Differenzierung implementiert | Ja | Code Review |
| Falsche Negative (echter Ausfall als Info) | 0 | Testfälle |

## Nicht Bestandteil
- Kein globales Observability Backend (z.B. Sentry) implementiert
- Keine Circuit Breaker Logik Beyond Basic Fallbacks
- Keine automatisierte Eskalation (Mail/Alert)

## Risiken & Mitigation
| Risiko | Beschreibung | Mitigation |
|--------|--------------|-----------|
| Fehler "verschluckt" | Rückgabe leere Liste maskiert Ursache | Logging weiterhin voll, Panel klar formuliert |
| Staleness Schwelle falsch | Zu sensible Warnungen | Feinjustierung via Konstante / Config |
| UX Überladen | Zu viele Panels gleichzeitig | Priorisierungslogik (hard failure > warn > info) |

## Erweiterungen (Future)
- Integration Sentry / OpenTelemetry
- Circuit Breaker bei wiederholtem DB Fail
- Unterscheidung "Keine Daten je" vs. "Gefilterter Bereich leer"

## Nachweis Verbesserung (Qualitativ – fokussiert auf implementierte Teile)
Vorher: Ungefangene DB-Ausfälle führten zu unklaren UI-Zuständen / potentiellen Abstürzen.
Nachher: DB-Ausfälle resultieren in sauberem Fehlerpanel statt Crash; fehlerhafte Selektionsabfragen liefern leere Listen (UI bleibt renderbar). Staleness-Erkennung verfügbar, aber Präsentation noch nicht einheitlich.

## Offene Lücken / Next Steps
- Konsistente Nutzung von `st.info` für "noch keine Daten" statt stillem Leerlauf
- Einführung optionaler Erfolgstoasts nach erstem validen Datensatz
- Externe API Fallback (Standardisierte Info Meldung)
- Zentralisiertes Severity-Mapping Utility
- Optionale Telemetrie (Sentry / OTel) zur Messung ungefangener Ausnahmen
