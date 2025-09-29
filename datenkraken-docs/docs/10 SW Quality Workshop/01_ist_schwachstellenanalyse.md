# 1. Ist- & Schwachstellenanalyse

Ziel dieser Analyse ist es, den aktuellen Zustand der Produkt- und Prozessqualität strukturiert zu erfassen, Lücken zu ISO/IEC 25010 sowie internen Qualitätszielen aufzuzeigen und eine priorisierte Basis für Optimierungen zu schaffen.

## 1.1 Bezugssysteme
- ISO/IEC 25010 (Product Quality & Quality in Use)
- Projektinterne Quality Goals (arc42 Kapitel "Introduction and Goals")
- SFMEA (Start & End Version) als Risikotreiber
- Deployment & Betriebsartefakte (Docker, Monitoring, Backup)
- Entwicklungsprozess (Definition of Done, Tests, Boards)

## 1.2 Bewertete Qualitätsmerkmale (Auswahl & Relevanz)
| ISO 25010 Merkmal | Relevanz Begründung | Aktueller Reifegrad | Primäre Evidenz |
|------------------|---------------------|---------------------|-----------------|
| Functional Suitability | Korrekte Erfassung & Darstellung von Raumklimadaten | Mittel | Funktionsanforderungen FR.1.x, UI Seiten |
| Reliability (Availability, Fault Tolerance) | Datenpipeline darf kurzzeitige Ausfälle überstehen | Niedrig-Mittel (teils manuell) | Fehlende automatische Alertings, einfache Retry-Konzepte |
| Performance Efficiency | Daten müssen <5 Min im Gold Layer sein | Mittel | NFR.1.1, noch keine Ende-zu-Ende Metrik dokumentiert |
| Compatibility | Komponenten via MQTT/DB | Hoch (technisch simpel gekoppelt) | Klare Schnittstellen (Topics, Tabellen) |
| Usability (Accessibility) | Tastaturlos bedienbar (NFR.3.1) | Teilweise belegt (rudimentäre Tests) | `frontend/tests/accessibility/test_accessibility.py` prüft Abwesenheit von Text-/Number-/Textarea Inputs, jedoch kein vollständiger Audit |
| Security | Sensordaten, interne Infrastruktur | Basismaßnahmen, keine Hardening-Doku | Fehlende Threat Model / Auth-Layer |
| Maintainability | Änderbarkeit & Testbarkeit | Mittel (strukturierte Module, aber Coding Standards inkonsistent) | Inkonsistenzen Benennung, teils fehlende Tests |
| Portability (Deployability) | Einfaches Aufsetzen für neue Umgebung | Verbessert (Gesamt-Compose geplant) | Bisher einzelne Compose für jeden Service |

## 1.3 Interne Qualitätsziele vs. Umsetzung
| Quality Goal aus arc42 | Verknüpfte Failure Modes (SFMEA) | aktueller Stand | Gap |
|------------------------|-------------------------------|-----------------|-----|
| Data Quality (NFR.1.1) | FA7, FA9, FA5, FA6, FA12 | Teilweise adressiert, kein End-to-End Lead Time Tracking | Messbarkeit fehlt |
| DB Availability 95% (NFR.1.2) | FA9, FA12 | Uptime-Skript vorhanden, keine automatische Eskalation | Kein Alerting/Trendreport |
| Accessibility (NFR.3.1) | (None) | Nicht belegt | Fehlende Nachweise & Testfälle |

## 1.4 Artefakt-Abgleich (Board / Doku / Code)
| Aspekt | Beobachtung | Risiko |
|--------|-------------|-------|
| SFMEA -> Korrekturmaßnahmen | Teilweise nicht rückverlinkt in Code Commits | Gefahr der Erosion | 
| Backup Konzept | Restore-Pfad nicht dokumentiert | Schein-Sicherheit | 
| Mock-Daten | Veraltet gegenüber DB-Schema | Falsche Testannahmen | 
| Error Handling Frontend | Jetzt systematisch (Panels, Fallbacks) | Vorher White-Screen / Developer Trace | 
| Deployment | Manueller Multi-Step Prozess | Onboarding-Latenz, Fehleranfälligkeit |
| Definition of Done | Unklar / nicht operationalisiert | Qualität variiert zwischen Stories |

## 1.5 Identifizierte Schwachstellen (Kurzliste)
1. Fehlendes aktives Alerting (Arduino Offline / Datenfluss Stillstand)
2. Veraltete Mock-Daten -> inkonsistente Testläufe
3. Fehlende dokumentierte Restore-Prozedur trotz Backup-Skript
4. Unvollständige Prozessdefinition (DoD nicht verankert)
5. Fehlende Metrik für End-to-End Datenlatenz (Sensor -> Gold Layer)
6. Eingeschränkte Testabdeckung Arduino (Fehler- & Randfälle)
7. Fehlende Accessibility-Verifikation (NFR.3.1)

## 1.6 Detaillierte Schwachstellenanalyse
### 1.6.1 Alerting Lücke
- Symptom: Keine aktive Benachrichtigung bei Ausbleiben von MQTT Messwerten.
- Wirkung: Verzögerte Fehlererkennung, Risiko Datenlücken > definierter Toleranz.
- Bezug: SFMEA FA1, FA5, FA6 (Detection oft Dormant/Hidden).
- Impact: Hoch (verhindert proaktives Handeln), Aufwand: Mittel.

### 1.6.2 Inkonsistente Mock-Daten
- Symptom: Testdaten reflektieren Schemaänderungen nicht.
- Wirkung: Falsche UI-Annahmen, fehlgeleitete Performance-Einschätzung.
- Impact: Mittel, Aufwand: Niedrig-Mittel (Skripte + Validierung).

### 1.6.3 Fehlende Restore-Doku
- Symptom: Nur Backup beschrieben.
- Wirkung: Risiko nutzloser Backups ("Restore Gap").
- Impact: Mittel (Recovery-Zeit verlängert), Aufwand: Niedrig.

### 1.6.4 DoD Unschärfe
- Symptom: Kein konsistenter Qualitäts-Gating Mechanismus.
- Wirkung: Variierende Merge-Qualität, fehlende Nachvollziehbarkeit.
- Impact: Mittel, Aufwand: Niedrig.

### 1.6.5 Fehlende Latenz-Metrik
- Symptom: Keine Messung vom Zeitpunkt Arduino-Send bis Daten verfügbar.
- Wirkung: NFR.1.1 nicht verifizierbar.
- Impact: Hoch für Audits, Aufwand: Mittel (Timestamp-Korrelation + Pipeline Metric).

### 1.6.6 Arduino Testabdeckung
- Symptom: Rand-/Fehlerfälle fehlen.
- Wirkung: Silent Failures möglich.
- Impact: Mittel, Aufwand: Mittel-Hoch.

### 1.6.7 Accessibility Validierung
- Symptom: Nur sehr rudimentäre Tests (Abwesenheit von Texteingaben) vorhanden, kein umfassender Accessibility / Interaction Audit.
- Evidenz: `frontend/tests/accessibility/test_accessibility.py` (prüft, dass keine text_input/number_input/textarea Widgets vorhanden sind → Fokus auf maus-/touch-only Bedienung, aber keine Prüfung von z.B. Fokus-Reihenfolge, ARIA Rollen, Kontrast, Screenreader-Verhalten).
- Wirkung: NFR.3.1 nur teilweise belegt; Risiko von verdeckten Barrieren (z.B. fehlende Alternativtexte, semantische Struktur).
- Impact: Niedrig-Mittel (Dashboard-Funktionalität begrenzt komplex, aber Nachweis lückenhaft), Aufwand: Mittel (automatisierbare Checks + manuelle Heuristikprüfung).
- Verbesserungspotenzial:
	- Ergänzung automatisierter Checks (z.B. Pa11y / axe-core gegen gerenderte Streamlit Seite via Playwright)
	- Manuelle Checkliste (Kontrast, Fokusindikator, Responsive Bedienbarkeit)
	- Dokumentation der Nicht-Anforderungen (falls Keyboard optional aber nicht ausgeschlossen) zur Klarstellung.

## 1.7 Priorisierte Fokusthemen für Optimierung
| ID | Thema | Begründung Auswahl | Optimierung im Scope? |
|----|-------|--------------------|-----------------------|
| A1 | Mock-Daten Aktualisierung | Schneller Qualitätshebel, reduziert Fehlinterpretationen | Ja |
| A2 | Docker Compose Deployment | Erhöht Reproduzierbarkeit & senkt Einstiegskosten | Ja |
| A3 | Frontend Error Handling | Direkt spürbare Qualitäts-/UX Verbesserung | Ja |
| A4 | Arduino Offline Alerting | Kritisches fehlendes Feature (Detection) | Ja (als neues Feature) |
| A5 | Restore-Doku | Wichtig, aber außerhalb Kern-Dreiklang | Nachgelagert |
| A6 | DoD Präzisierung | Prozessqualität Folgeiteration | Nachgelagert |
| A7 | Latenz-Metrik | Technisch aufwändiger (Ende-zu-Ende) | Nachgelagert |

## 1.8 Messbarkeits-Vorschläge (Metriken)
| Ziel | Vorschlag Metrik | Erfassungsmethode |
|------|------------------|-------------------|
| Datenlatenz | P95 End-to-End (Arduino Timestamp -> Gold Row Timestamp) | Log Korrelation + Timescale Funktion |
| Availability DB | % Minuten mit erfolgreichem Health Check | Uptime Skript Aggregation |
| Fehlerrobustheit UI | # ungefangene Exceptions / Session | Logging + Test Harness |
| Mock-Daten Qualität | Schema-Diff Count = 0 | Automatisierter Vergleich (introspect DB vs. sample JSON) |
| Deployment Reproduzierbarkeit | Zeit Onboarding -> Erstes Dashboard | Developer Self-Report + Timer |
| Alerting Wirksamkeit | Mean Time To Detect (MTTD) Ausfall Arduino | Simulierter Ausfall + Timestamp Differenz |

## 1.9 Zusammenfassung
Das System besitzt eine solide Basis in Funktionsabdeckung und modularer Struktur. Die größten Lücken liegen in: (1) fehlender aktiver Überwachung (Alerting), (2) Qualitätsabsicherung durch repräsentative Test-/Mock-Daten und (3) Vereinheitlichung von Deployment & Fehlertoleranz an der UI. Die ausgewählten Optimierungen adressieren unmittelbar Risiko, Transparenz und Nutzungsqualität.
