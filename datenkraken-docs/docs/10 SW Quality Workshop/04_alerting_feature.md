# New Feature: Arduino Offline Alerting

Goal: Early detection of pipeline outages or stalls (Arduino → MQTT → subscription → DB) via active alerting for missing or inconsistent messages.

## Problem & motivation
Initial (pre‑implementation): No active notification when MQTT measurements stop or sequence errors occur → reactive recognition (empty UI / latency until human notice).

Current implemented state:
- Inactivity watchdog thread in `subscription_script/main.py` tracks time since last message (`get_last_message_timestamp`).
- Email alert on exceeding `WATCHDOG_INACTIVITY_THRESHOLD_SECONDS`, plus recovery mail when flow resumes.
- Sequence anomaly alert (`send_sequence_alert`) with separate cooldown keying (`seq:{topic}`).
- Cooldown & force logic in `alerting.py` core `send_alert_email`.

NOT implemented yet:
- Persistent status table (`sensor_status`), event history (`alert_events`).
- UI status badges / user threshold & recipient configuration.
- Explicit heartbeat messages (currently inferred via normal data flow).

Impacted failure modes (extended): FA1, FA5, FA6, FA13 (new), secondary FA7.

## Scope (current vs. target)
| Aspect | Current implementation | Target vision |
|--------|-----------------------|--------------|
| Inactivity detection | Time since last MQTT msg (watchdog threshold) | Add persistent status + MTTD metric |
| Sequence monitoring | Email on gap anomaly | Correlate w/ persistent sequence history / gap count |
| Delivery channel | Email only | Extend (webhook / Slack) |
| Configuration | Env vars (`ALERT_*`, `WATCHDOG_*`) | UI form + DB persistence |
| Persistence | None (in‑memory cooldown registry only) | `sensor_status`, `alert_events` tables |
| UI visualization | None | Badges (online / offline / degraded) |
| Heartbeat | Implicit (data flow) | Explicit dedicated topic (optional) |

## Actual implemented flow (subscription script)
1. MQTT message arrival updates last timestamp & sequence state (`on_message`).
2. Background thread `_watchdog_loop` (1s interval) evaluates inactivity duration.
3. If threshold exceeded → `send_inactivity_alert` once; sets `_inactivity_alert_active`.
4. When flow resumes → `send_inactivity_recovery_alert`; flag reset.
5. Sequence deviation (expected vs. received) → `send_sequence_alert` (per-topic cooldown).
6. SMTP misconfiguration / missing recipients → single warning, no crash.

No persistent storage of state transitions – only logs & emails.

## Target architecture (future extensions)
1. Persistent status table (`sensor_status`): `room_id`, `last_seq`, `last_timestamp`, `state`.
2. Event table (`alert_events`): history including `from_state`, `to_state`, `created_at`.
3. UI badge + history view + configuration surface (threshold / recipients / gap tolerance).
4. Optional heartbeat messages to reduce false positives during natural idle windows.

## Component overview (current vs. target)
| Component | Current role | Target (extended) role |
|-----------|--------------|------------------------|
| Arduino | Emits measurements (implicit heartbeat) | Optional explicit heartbeat |
| Subscription script | Watchdog + email sending | Add persistence & metrics export |
| DB | Store measurements | Add status + event history |
| Frontend | (No alert UI) | Config + status display |
| Mailer | SMTP delivery | Multi‑channel abstraction |

## State logic (target model – not implemented)
| Condition | State |
|-----------|-------|
| now - last_timestamp <= threshold AND no seq gap | online |
| now - last_timestamp > threshold | offline |
| now - last_timestamp <= threshold AND seq gap detected | degraded |

Current implementation: binary inactivity + recovery (no explicit degraded state).

## Acceptance criteria (current vs. target)
| Criterion | Current | Target |
|-----------|---------|--------|
| Offline detection | Inactivity > threshold → alert | Keep + persistence |
| Sequence gap detection | Email alert (no state category) | Degraded state + event |
| One alert per outage | Implemented (flag) | + Persistent outage ID |
| Configurability | Env variables | UI + DB settings |
| Persistent history | None | `alert_events` table |
| MTTD measurable | Only indirect (logs) | Prometheus metric export |

## Metrics (target – not implemented)
| Metric | Target |
|--------|--------|
| Mean Time To Detect (MTTD) | < 2× threshold |
| False positives / week | ≤ 1 |
| Recovery recognition time | < 1 min |

## Risks & mitigation
| Risk | Description | Countermeasure |
|------|------------|---------------|
| Flapping | Frequent state toggles | Hysteresis (2 consecutive checks) |
| Mail failure | SMTP unreachable | Retry + log + status flag |
| Sequence reset | Arduino reboot lowers seq | Detect reset (seq smaller & fresh timestamp) |
| Clock drift | Unsynced clock | Ensure NTP / server time source |

## Extensions (backlog)
- Multi‑channel alerts (Slack / webhook)
- Aggregated daily reports
- Drift detection (FA14) / quality degradation observability
- Prometheus exporter for status & counts
- Persistent state machine + UI badges

## RPN assessment (current contribution vs. target)
| Failure Mode | Base RPN | Current implementation contribution | Limitation | Target model potential |
|--------------|---------|------------------------------------|------------|----------------------|
| FA13 Offline not detected | 256 | Inactivity alert reduces detection delay | No persistence / metric | Further reduction via state persistence + MTTD tracking |
| FA5 Data not transferred | 192 | Sequence alerts surface gaps | No correlation with DB write failures | Combine with write result counters |
| FA6 Reception disturbed | 189 | Indirect detection (inactivity) | No cause differentiation | Cause‑specific classification (broker vs. publisher) |

## Summary
Implemented: minimal but effective core (inactivity + recovery + sequence anomaly alerting) without persistence & UI integration. Original broader vision now clearly marked as future. Next steps: persistent status tracking, UI visualization, metric export.
