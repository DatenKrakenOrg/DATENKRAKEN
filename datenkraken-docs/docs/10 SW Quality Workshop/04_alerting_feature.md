# 4. Neues Feature: Arduino Offline Alerting

Ziel: Früherkennung von Ausfällen oder Hängern der Sensordaten-Pipeline (Arduino → MQTT → Subscription → DB) durch aktives Alerting bei fehlenden oder inkonsistenten Nachrichten.

## 4.1 Problem & Motivation
Ausgangspunkt (vor Implementierung): Keine aktive Meldung bei Ausbleiben von MQTT Messungen oder Sequenzfehlern → reaktive Sicht (leere UI / Latenz bis Erkennung).

Realer aktueller Stand (Implementiert):
- Inactivity Watchdog Thread im `subscription_script/main.py` misst Zeit seit letztem MQTT Message Timestamp (`get_last_message_timestamp`).
- E-Mail Versand bei Überschreitung von `WATCHDOG_INACTIVITY_THRESHOLD_SECONDS` (einmalig) und Recovery-Mail, wenn Daten wieder eintreffen.
- Sequenz-Anomalie Alert (`send_sequence_alert`) über separates Cooldown-Prinzip (`seq:{topic}` Keys).
- Cooldown & Force-Mechanismus im `alerting.py` (zentrale Funktion `send_alert_email`).

Noch NICHT umgesetzt:
- Persistente Status-Tabelle (`sensor_status`), Event-Historie (`alert_events`).
- UI Status Badges / Konfiguration von Schwellen & Empfängern.
- Heartbeat auf Ebene Arduino (explizite Heartbeat Messages statt Inferenz aus Datenfluss).

Betroffene Failure Modes (erweitert): FA1, FA5, FA6, FA13 (neu), sekundär FA7.

## 4.2 Scope (Realer Stand vs. Ziel)
| Aspekt | Real umgesetzt | Zielbild |
|--------|----------------|---------|
| Inactivity Detection | Zeit since last MQTT msg (Watchdog, Threshold) | Ergänzt um persistente Status-Tabelle & MTTD Monitoring |
| Sequence Monitoring | E-Mail bei Lücke (Anomalie) | Korrelation mit persistenter Sequenz-Historie / Gap Count |
| Versandkanal | Nur E-Mail | Erweiterbar (Webhook/Slack) |
| Konfiguration | Env Variablen (`ALERT_*`, `WATCHDOG_*`) | UI Formular + DB Persistenz |
| Persistenz | Keine (nur in-memory Cooldown Registry) | `sensor_status`, `alert_events` Tabellen |
| UI Visualisierung | Keine | Badges (online/offline/degraded) |
| Heartbeat | Implizit (Datenfluss) | Explizit (separates Topic optional) |

## 4.3 Real implementierter Ablauf (Subscription Script)
1. MQTT Message Empfang setzt internen letzten Timestamp & Sequenztracking (via `on_message`).
2. Hintergrund-Thread `_watchdog_loop` (1s Intervall) berechnet Inaktivitätsdauer.
3. Überschreitet die Dauer den Threshold → `send_inactivity_alert` (einmal) + setzt Flag `_inactivity_alert_active`.
4. Datenfluss kehrt zurück → `send_inactivity_recovery_alert` + Flag Reset.
5. Sequenzabweichungen (Erwartet vs. Erhalten) → `send_sequence_alert` (Cooldown-pro-Topic).
6. Fehlkonfiguration SMTP / fehlende Empfänger → einmalige Warning, kein Crash.

Keine dauerhafte Speicherung dieser Zustandswechsel – ausschließlich Logs & E-Mails.

## 4.4 Zielbild (Erweiterungsperspektive)
1. Persistente Status-Tabelle (`sensor_status`) mit Spalten: `room_id`, `last_seq`, `last_timestamp`, `state`.
2. Event-Tabelle (`alert_events`) für Historie, inklusive `from_state`, `to_state`, `created_at`.
3. UI Badge + Historienansicht + Config Oberfläche (Threshold / Empfänger / Gap Toleranz).
4. Optionale Heartbeat Messages bei Absenz regulärer Daten (reduziert False Positives bei natürlicher Mess-Pause).

## 4.5 Komponentenübersicht (Ist vs. Ziel)
| Komponente | Ist Rolle | Ziel Rolle (Erweiterung) |
|------------|----------|--------------------------|
| Arduino | Liefert Messdaten (impliziter Heartbeat) | Optionale Heartbeat Messages |
| Subscription Script | Watchdog + E-Mail Versand | Ergänzt um Status Persist & Metrics Export |
| DB | Speicherung Messwerte | Zusätzlich Status & Event Historie |
| Frontend | (Kein Alert UI) | Konfiguration & Statusanzeige |
| Mailer | SMTP Versand | Multi-Channel Abstraktion |

## 4.6 Zustandslogik (Zielmodell – nicht umgesetzt)
| Bedingung | State |
|-----------|-------|
| now - last_timestamp <= threshold AND keine Seq-Lücke | online |
| now - last_timestamp > threshold | offline |
| now - last_timestamp <= threshold AND Seq-Lücke erkannt | degraded |

Aktuell existiert nur eine binäre Inaktivität mit Recovery (kein expliziter "degraded" Status).

## 4.12 Akzeptanzkriterien (Ist vs. Ziel)
| Kriterium | Ist | Ziel |
|-----------|-----|------|
| Offline Detection | Inaktivität > Threshold → Alert | Beibehalten + Persistenz |
| Seq Gap Detection | E-Mail Alert (keine State-Kategorie) | Degraded State + Event |
| Einmaliger Alert je Ausfall | Implementiert (Flag) | + Persistente Outage-ID |
| Konfigurierbarkeit | Env Variablen | UI + DB Settings |
| Persistente Historie | Nicht vorhanden | `alert_events` Tabelle |
| MTTD Messbar | Nur indirekt (Logs) | Metrik Export (Prometheus) |

## 4.13 Metriken (Ziel – nicht umgesetzt)
| Metrik | Ziel |
|--------|-----|
| Mean Time To Detect (MTTD) | < 2×Threshold |
| False Positives / Woche | <= 1 |
| Recovery Recognition Zeit | < 1 Min |

## 4.13 Risiken & Mitigation
| Risiko | Beschreibung | Gegenmaßnahme |
|--------|--------------|---------------|
| Flapping | Häufige State-Wechsel | Hysterese (2 konsekutive Checks) |
| Mail Failure | SMTP nicht erreichbar | Retry + Log + Status Flag |
| Seq Reset | Arduino Neustart setzt seq zurück | Erkennung Reset (seq kleiner & Zeit frisch) |
| Zeitdrift | Unsynchronisierte Uhr | NTP Sicherstellen / Serverzeit maßgeblich |

## 4.14 Erweiterung (Backlog)
- Multi-Channel Alerts (Slack / Webhook)
- Aggregierte Tagesreportings
- Drift-Erkennung (FA14) / Quality Degradation Observability
- Prometheus Exporter für Status & Counts
- Persistente State Machine + UI Badges

## 4.15 RPN-Einschätzung (aktueller Beitrag vs. Ziel)
| Failure Mode | Ausgang RPN | Beitrag aktuelle Implementierung | Limitierung | Potenzial Zielmodell |
|--------------|------------|----------------------------------|-------------|----------------------|
| FA13 (Neu) Offline nicht erkannt | 256 | Reduktion durch Inactivity Alert (Detection ↑) | Keine Persistenz / Metrik | Weiter Reduktion durch State Persist + MTTD Tracking |
| FA5 Daten nicht transferiert | 192 | Sequenz Alerts machen Lücken sichtbar | Keine Korrelation mit DB Write Errors | Kombination mit Write Result Counters |
| FA6 Empfang gestört | 189 | Indirekte Erkennung (Inaktivität) | Keine Unterscheidung Ursache | Ursache-spezifische Klassifikation (Broker vs. Publisher) |

## 4.16 Zusammenfassung
Aktuell implementiert: Minimaler, aber wirkungsvoller Kern (Inactivity + Recovery + Sequenz-Anomalie Alerting) ohne Persistenz & UI Integration. Das ursprüngliche Dokument beschrieb ein weitergehendes Zielbild – dieses ist jetzt explizit als zukünftige Erweiterung markiert. Nächste sinnvolle Schritte: Persistente Statusführung, UI Visualisierung, Metrikexport.
