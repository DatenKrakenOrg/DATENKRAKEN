# 2. Erweiterte SFMEA & Vergleich

Dieses Kapitel ergänzt und reflektiert die vorhandenen SFMEA-Stände (Projektstart & Projektende). Fokus: Konsistenz, Veränderungen der RPN, verbleibende Lücken (v.a. Detection) und Ableitung zusätzlicher Maßnahmen (insb. Alerting & Datenvalidierung).

## 2.1 Vergleich Überblick
| Aspekt | Start-SFMEA | End-SFMEA | Beobachtung |
|--------|-------------|----------|-------------|
| Umfang Komponenten | Arduino, Subscription, DB (UI WIP) | UI hinzugekommen | Vollständiger Systemblick erreicht |
| RPN Spitzenwert | 216 (FA7) | 210 (FA2 bleibt hoch, FA7 reduziert) | Maßnahmen teils wirksam (FA7) |
| Detection Klassifizierung | Viele Dormant/Hidden (Übertragungskette) | Teilweise Evident für Subscription | Keine aktive Benachrichtigung bei Ausfällen |
| Fokus Korrekturmaßnahmen | Retry, Kalibrierung, Caching | Prioritätsreduktionen dokumentiert | Wirksamkeit nur teilweise quantifiziert |

## 2.2 Auffälligkeiten & Plausibilitätscheck
- FA2 (Sensor-Inaccuracy) unverändert hoch -> Keine belegten Kalibrier- oder Drift-Erkennungsmechanismen in Doku.
- FA6/FA7 Detection Wechsel (Hidden→Evident) im Endstand nicht ausreichend begründet (fehlende Log-/Monitoring-Verweise).
- RPN Reduktion FA7 (216→96) erscheint stark – ohne persistenten Queue/Puffer-Nachweis riskant.
- Fehlender Eintrag für "Arduino Offline Detection" als eigener Failure Mode (z.B. FA13) → wird über FA1/FA5 indirekt abgedeckt aber unpräzise.

## 2.3 Ergänzte Failure Modes / Verfeinerung
| ID Neu | Komponente | Failure Mode | Ursache | Effekt | Bemerkung |
|--------|------------|--------------|---------|--------|-----------|
| FA13 | Monitoring / Alerting | Ausfall von Datenstrom bleibt unbemerkt | Kein Heartbeat / Timeout | Verzögerte Fehlerreaktion, Datenlücke | Splittet Erkennungsaspekt von FA1/FA5 |
| FA14 | Datenqualitätspipeline | Unkalibrierte Drifts unentdeckt | Sensoralterung | Schleichend falsche Empfehlungen | Ergänzt FA2 um zeitliche Dimension |
| FA15 | Prozess | Unvollständiger Merge (fehlende Tests/Doku) | Unschärfe DoD | Erhöht Einführungsfehler | Prozessrisiko, wirkt indirekt auf mehrere FAs |

## 2.4 Neue/Erweiterte Bewertung (Auszug)
| ID | S | O | D | RPN | Begründung (Detection Fokus) |
|----|---|---|---|-----|------------------------------|
| FA13 | 8 | 4 | 8 | 256 | Höchster RPN – derzeit keine aktive Erkennung (nur reaktive Sicht) |
| FA14 | 6 | 5 | 7 | 210 | Drift schwer erkennbar ohne Validierungsroutine |
| FA15 | 5 | 5 | 6 | 150 | Prozesslücke führt zu Qualitätsfluktuation |

Damit verschiebt sich der kritische Hotspot klar zu FA13 (Alerting-Lücke) – dies rechtfertigt das neue Feature.

## 2.5 Maßnahmen-Matrix (Alt vs. Neu)
| Failure Mode | Vorhandene Maßnahme | Lücke | Ergänzungsvorschlag |
|--------------|---------------------|-------|---------------------|
| FA2 | Kalibrierung (unspezifisch) | Kein Intervall, keine Drift-Metrik | Quartals-Kalibrier-Check + Plausibilitätsprüfung (Median-Profil) |
| FA5 | ACK/Retry | Keine Sequenzüberwachung | Sequenznummer + Backoff + Offline Counter |
| FA7 | Queue/Buffer (behauptet) | Kein Artefaktnachweis | Persistenter Replay-Puffer (lokale SQLite) |
| FA9 | Caching & Reconnect | Keine Timeout-Metriken | Health Endpoint + Prometheus Counter |
| FA13 (neu) | (—) | Kein Timeout definiert | Heartbeat-Intervall + Offline Alert (Mail) |
| FA14 (neu) | (—) | Keine Drift-Metrik | Rolling z-Score / IQR Ausreißerstatistik |
| FA15 (neu) | (—) | DoD nicht verbindlich | Checklisten-Gate PR Template |

## 2.6 Reduzierte RPN Prognose nach Umsetzung Alerting
| Mode | Ausgang RPN | Maßnahme | Erwartete Änderung (D oder O) | Ziel-RPN |
|------|-------------|----------|-------------------------------|----------|
| FA13 | 256 | Heartbeat (Topic) + 5-Min Timeout + Mail Alert | D: 8→3 | 96 |
| FA5 | 192 | Sequenz + Retransmit | D: 6→4 | 128 |
| FA2 | 210 | Quartals-Kalibrierung + Driftstatistik | O:6→4, D:5→4 | 112 |

## 2.7 Begründung Alerting Feature Priorität
- Höchster neu identifizierter RPN (FA13)
- Niedrige Implementierungskomplexität (MQTT Timeout + Mail Versand)
- Hebt gleich mehrere Failure Modes in Detection (FA1, FA5, FA6)
- Schafft messbare Metrik (MTTD)

## 2.8 Qualitäts-Sicherungs-Hooks (Empfohlen)
| Ebene | Mechanismus | Zweck |
|-------|-------------|------|
| MQTT Ingestion | Last Timestamp Cache | Offline Detection |
| Subscription Script | Sequence Validator | Paketverlust / Reordering |
| DB Layer | Write Result Counter | Frühes Erkennen von Persistenzfehlern |
| Frontend | Staleness Badge | Transparenz Data Freshness |
| Prozess | PR Checklist | DoD Durchsetzung |

## 2.9 Zusammenfassung
Die ursprüngliche SFMEA bildet zentrale Datenflussrisiken ab, unterschätzt jedoch systematisch die Erkennungslücken (Detection) und Prozessrisiken. Die Erweiterung mit FA13–FA15 schärft die Priorisierung. Das geplante Alerting-Feature adressiert eine strukturelle Blindheit und verschiebt den Risikogipfel deutlich nach unten. Folgearbeiten sollten Drift-Erkennung (FA14) und Prozess-Härtung (FA15) betreffen.
