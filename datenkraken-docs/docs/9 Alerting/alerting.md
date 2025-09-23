# Alerting & Monitoring (Subscription Script)

This document describes the runtime alerting features implemented in the **subscription_script** component. Its goal is to detect data ingestion problems early and notify operators via e-mail.

## 1. Overview
The subscription script ingests sensor data from MQTT and writes it to TimescaleDB. Two failure classes are monitored:

1. Inactivity (no MQTT messages for a configurable time window)
2. Sequence anomalies (skipped or repeated sequence numbers per sensor topic)

Notification channel: SMTP e-mail (one alert + one recovery per inactivity window, rate-limited alerts for sequence anomalies).

## 2. Features
- Per-topic sequence tracking (`temp`, `hum`, `co2`/VOC, `mic`)
- Automatic baseline detection for the first observed sequence (prevents false positives when the consumer starts late)
- Inactivity watchdog thread with a threshold (default 300s unless overridden by env)
- Inactivity alert only once per outage, plus an explicit recovery e-mail when data resumes
- Cooldown-based sequence anomaly alerting (per topic key)
- Graceful failure (alert sending errors never crash ingestion)
- Support for implicit SSL SMTP (port 465) and STARTTLS (e.g. port 587)

## 3. Sequence Monitoring
Each sensor category maintains its last seen sequence number. On every new message:
1. If last stored sequence is 0 (initial), the current value becomes the baseline (info log only)
2. Else the expected number is `last + 1`
3. If the received number differs → warning log + sequence alert (subject: "MQTT Sequence Anomaly")

This helps detect dropped messages or publisher restarts that reset counters unexpectedly.

### Limitations
- Baseline resets on process restart (no persistent state). For strict global continuity you would need external storage.
- Mixed ordering across topics is not correlated (each topic family is independent).

## 4. Inactivity Watchdog
A background thread records the timestamp of the last received MQTT message (even if payload JSON is malformed). Steps:
1. Every second the thread checks `now - last_message_ts`.
2. If the difference exceeds the threshold (`WATCHDOG_INACTIVITY_THRESHOLD_SECONDS`) and no active alert → send Inactivity Alert (one time) and mark outage active.
3. When messages resume (difference below threshold) and outage was active → send Recovery Alert and clear state.

### Rationale
Avoids spam during prolonged outages and gives a clear start/end signal.

## 5. Configuration (Environment Variables)
| Variable | Description | Default |
|----------|-------------|---------|
| `WATCHDOG_INACTIVITY_THRESHOLD_SECONDS` | Seconds without any MQTT message before inactivity alert | 300 (example) |
| `ALERT_COOLDOWN_SECONDS` | Cooldown for sequence anomaly alerts per topic key | 300 |
| `SMTP_HOST` | SMTP server hostname | (required for e-mail) |
| `SMTP_PORT` | SMTP server port (465 implicit SSL, 587 STARTTLS) | 587 |
| `SMTP_USER` | SMTP auth username | optional |
| `SMTP_PASS` | SMTP auth password | optional |
| `ALERT_EMAIL_FROM` | From address (fallback: `SMTP_USER`) | derived |
| `ALERT_EMAIL_TO` | Comma separated recipient list | (required) |

### Example (.env excerpt)
```
SMTP_HOST=mail.example.org
SMTP_PORT=465
SMTP_USER=alerts@example.org
SMTP_PASS=secret
ALERT_EMAIL_FROM=alerts@example.org
ALERT_EMAIL_TO=ops@example.org,dev@example.org
WATCHDOG_INACTIVITY_THRESHOLD_SECONDS=300
ALERT_COOLDOWN_SECONDS=600
```

## 6. E-mail Flow
| Scenario | Mail(s) Sent | Notes |
|----------|--------------|-------|
| Inactivity begins | 1x Inactivity Alert | Only once until recovery |
| Continued inactivity | none | Outage flagged active |
| Data resumes | 1x Recovery Alert | Resets state |
| Sequence anomaly | Sequence Anomaly Alert | Subject key per topic, respects cooldown |

## 7. Error Handling
- SMTP errors are logged with level ERROR; ingestion continues.
- If TLS negotiation fails for STARTTLS, code falls back to plain unless mode is strictly SSL (implicit via port 465).
- Missing config (no recipients or host) logs a single warning and disables sending.
