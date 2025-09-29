# SFMEA Iteration 3 (Enhanced / Post-Mitigation View)

Scale reminder:
- S (1–10): Impact (10 = severe system loss / regulatory critical)
- O (1–10): Likelihood (10 = almost inevitable)
- D (1–10): Detectability (10 = NOT likely to be detected)
- RPN = S × O × D (Higher ⇒ riskier). Post‑mitigation RPN (Residual) shown separately.

---
## Legend
Detection classification tags used in commentary:
- Evident: Operator / automated alert immediately signals.
- Dormant: Only seen during routine review / manual check.
- Hidden: No signal unless specifically probed.

Action Category:
- Quick Win: Low effort (<0.5 day) high leverage.
- Strategic: Architectural / medium effort.
- Monitor: Accept – track metrics; revisit if conditions change.

---
## Consolidated Failure Mode Table (Current vs Target)

| ID | Component | Failure Mode | Primary Cause(s) | Local Effect | End Effect | Current Controls | S | O | D | RPN | Recommended Action (Delta Focus) | Target S | Target O | Target D | Residual RPN | Action Category |
|----|-----------|--------------|------------------|--------------|-----------|------------------|---|---|---|-----|----------------------------------|----------|----------|----------|--------------|----------------|
| FA1 | Arduino | Data Missing | Power loss, HW fault | No publish | Data gap in DB/UI | Basic logging; watchdog inactivity alert (indirect) | 8 | 5 | 4 | 160 | Add heartbeat topic + power stability (UPS) | 8 | 4 | 3 | 96 | Strategic |
| FA2 | Arduino | Data Inaccurate | Sensor drift, calibration loss | Wrong values | Misleading analytics | Future calibration procedure (not yet), plausibility checks WIP | 7 | 6 | 5 | 210 | Implement sensor self-test + range validation + trend deviation detection | 7 | 4 | 3 | 84 | Strategic |
| FA3 | Arduino | Data Timeless (bad timestamps) | NTP unreachable, clock reset | Stale/epoch ts | Misordered analytics & staleness misclassification | Sequence + staleness logic; no explicit clock drift alert | 6 | 3 | 6 | 108 | Add NTP sync watchdog & timestamp monotonicity check | 6 | 2 | 3 | 36 | Quick Win |
| FA4 | Arduino | Erroneous/Inconsistent datapoints | Environmental spikes | Outliers | Distorted aggregates | Planned anomaly detection (partial), sequence baseline | 7 | 4 | 4 | 112 | Deploy robust outlier filter + z-score / MAD thresholding | 7 | 3 | 3 | 63 | Strategic |
| FA5 | Arduino | Data cannot be transferred | WiFi/MQTT outage | Buffer growth / loss | Data gaps | Retry (implicit), watchdog inactivity detection | 8 | 4 | 5 | 160 | Add local queue w/ retry & backfill on reconnect | 8 | 3 | 3 | 72 | Strategic |
| FA6 | Subscription Script | Cannot receive from MQTT | Broker unreachable, net config | No incoming msgs | Data flow halt | Watchdog inactivity alert | 9 | 3 | 3 | 81 | Add broker multi-endpoint failover & exponential backoff metrics | 9 | 2 | 2 | 36 | Strategic |
| FA7 | Subscription Script | Cannot write to DB | DB down, network, auth | Insert failures | Data loss / backlog | Logging + future retry concept (not implemented), alerts partially (sequence only) | 9 | 4 | 6 | 216 | Introduce write queue + retry & alert on sustained failures | 9 | 3 | 3 | 81 | Strategic |
| FA8 | Database | Permanent outage | Host failure | No queries | System down | External infra monitoring only | 10 | 2 | 2 | 40 | Add automated failover / hot standby doc plan | 10 | 2 | 2 | 40 | Monitor |
| FA9 | Database | Temporary outage | Restart / maintenance / overload | Short unavailability | Transient data delay | Client retries partial, no caching | 7 | 5 | 6 | 210 | Add client retry with jitter + local cache | 7 | 3 | 3 | 63 | Strategic |
| FA10 | Database | Faulty data cleaning | Wrong view logic / timing | Incorrect derived data | Misleading analytics | Manual review; limited tests | 6 | 4 | 5 | 120 | Add unit tests + data quality assertions (row counts, null ratios) | 6 | 3 | 3 | 54 | Quick Win |
| FA11 | Database | Reading not possible | Permission, OOM, bad query | API errors | UI retrieval failures | UI error panels + health check fallback | 9 | 3 | 3 | 81 | Add query timeout + circuit breaker metrics | 9 | 2 | 2 | 36 | Quick Win |
| FA12 | Database | Writing not possible | Disk full, permissions, OOM | Inserts fail | Data loss risk | Logging only (no retry buffer) | 9 | 4 | 3 | 108 | Add disk usage monitoring + queued retry | 9 | 3 | 3 | 81 | Strategic |
| FA13 | Alerting Subsystem | Alert email not sent | SMTP auth/port issue | No notification | Operators unaware | Dual port handling + logging | 8 | 3 | 6 | 144 | Add send result health metric + fallback channel (webhook) | 8 | 2 | 3 | 48 | Quick Win |
| FA14 | Watchdog | False inactivity alert | Short burst gap, clock skew | Spurious email | Alert fatigue | Cooldown logic | 5 | 4 | 5 | 100 | Adaptive threshold (dynamic vs historical rate) | 5 | 3 | 3 | 45 | Strategic |
| FA15 | Sequence Tracking | Baseline mis-initialized | Startup after data gap | Missed anomaly | Undetected data discontinuity | First-message baseline acceptance | 7 | 3 | 7 | 147 | Persist last sequence per topic & check gap >1 on first after restart | 7 | 2 | 4 | 56 | Quick Win |
| FA16 | Frontend | Stale UI (silent) | Data fetch partial failure, caching | Misleading snapshot | Decisions on outdated data | Staleness widget + error panels | 6 | 4 | 4 | 96 | Add banner for >X min staleness + auto-refresh backoff | 6 | 3 | 3 | 54 | Quick Win |
| FA17 | Time Handling | Timezone / clock skew | Mixed TZ, DST issues | Mis-order, wrong staleness | Incorrect analytics | TZ normalization util | 6 | 3 | 5 | 90 | Add end-to-end time consistency test & drift alert | 6 | 2 | 3 | 36 | Quick Win |
| FA18 | DB Integrity | Silent partial writes | Transaction interruption | Missing subset rows | Subtle analytic bias | None (rely on DB atomicity, but multi-sensor batch risk) | 8 | 2 | 8 | 128 | Add row count reconciliation vs sequence continuity | 8 | 2 | 4 | 64 | Strategic |
| FA19 | Alerting | Email storm / spam | Rapid oscillation | Operator fatigue | Ignored future alerts | Cooldown registry | 6 | 3 | 3 | 54 | Add aggregated digest + escalation tiers | 6 | 2 | 2 | 24 | Monitor |
| FA20 | Analytics Quality | Outlier undetected | Gradual drift | Distorted trends | Inaccurate decisions | None full (basic guards only) | 6 | 5 | 7 | 210 | Implement statistical drift monitor (EWMA / z-score) | 6 | 3 | 4 | 72 | Strategic |

---
## Changes vs Iteration 2 (Highlights)
- Added eight new failure modes (FA13–FA20) covering alerting reliability, drift, integrity, UI staleness, and baseline weaknesses.
- Updated Detection scores where newly implemented watchdog, sequence anomaly detection, and UI error panels make failures more Evident (e.g., FA6 D 7→3 from start, further clarified).
- Separated Local vs End Effect to clarify containment possibilities.
- Reduced O for timestamp issues (FA3) acknowledging NTP is usually reliable but still giving moderate detectability penalty until explicit monitor exists.
- Differentiated DB outage permanent vs temporary and kept permanent as Monitor given low frequency and consistent detection.

---
## Scoring Rationale Examples
- FA7 (Write to DB failure): Severity remains 9 (data loss potential). Detection improved target D to 3 with queued retry + alert (not yet implemented, reflected in Target). Occurrence drops once transient retries smooth over small outages.
- FA15 (Sequence baseline): Hidden gap risk currently (D=7) because first jump after restart is accepted. Persisting last known sequence transforms it to Evident jump (D→4) and reduces O (fewer unobserved gaps).
- FA13 (Alert email failure): Without success metrics, detection is Dormant/Hidden. Adding delivery status & fallback (e.g., webhook / Slack) makes failure Evident (D→3).

---
## Priority Action Shortlist (Top Residual Risk Reduction per Effort)
Quick Wins (implement next sprint):
1. FA15 Persist last sequence per topic (avoid masked gaps)
2. FA10 Add data quality assertion tests for derived views
3. FA13 Add alert send metric + fallback channel
4. FA17 Add E2E time drift & TZ consistency test
5. FA11 Query timeout + circuit breaker
6. FA3 NTP sync watchdog & monotonic timestamp check

Strategic (plan & sequence):
1. FA7 Write queue & retry buffer (largest historic RPN driver)
2. FA2 Calibration + validation pipeline (drift governance)
3. FA9 Client caching + structured retry
4. FA5 Local queue on device for transfer outages
5. FA18 Row reconciliation & integrity audit
6. FA20 Statistical drift / anomaly monitoring framework

Monitor / Hold:
- FA8 Infrastructure failover (cost/benefit currently low)
- FA19 Digest / escalation (after volume justifies)
- FA14 Adaptive threshold (only if false alerts observed empirically)

---
## Action Tracking Template
(Use in issue tracker)
| Action | Owner | Effort (d) | Prereq | Status | Due |
|--------|-------|-----------|--------|--------|-----|
| Persist last sequence (FA15) | Backend | 0.3 | None | Planned | TBD |
| NTP watchdog (FA3) | Backend | 0.2 | None | Planned | TBD |
| Alert send metric + webhook (FA13) | Backend | 0.5 | SMTP logic | Planned | TBD |
| Data quality assertions (FA10) | Data | 0.3 | Test harness | Planned | TBD |
| Query timeout + circuit breaker (FA11) | Backend | 0.5 | Metrics infra | Planned | TBD |
| Time drift test (FA17) | Backend | 0.2 | None | Planned | TBD |
| Write queue & retry (FA7) | Backend | 1.5 | Metrics | Planned | TBD |
| Calibration & validation (FA2) | Hardware | 2.0 | Procedure draft | Planned | TBD |

---
## Residual Risk Distribution
Post-target residual RPN notable remaining items: FA7 (81), FA2 (84), FA5 (72), FA20 (72), FA12 (81) – all acceptable with monitoring but candidates for deeper architectural investment if risk appetite tightens.

---
## Notes & Critique of Earlier Iterations
- Duplicate header ("Failure Mode" repeated) removed to reduce ambiguity.
- Earlier detection labels (Hidden/Dormant) not always aligned with numeric D (e.g., Hidden yet D=6 vs others). This iteration ties Hidden ≈ D ≥7, Dormant ≈ 4–6, Evident ≤3.
- Lack of systematic new failure mode discovery around alerting & integrity – addressed by FA13–FA20.
- Previous corrective actions conflated detection improvement and likelihood reduction without distinguishing resulting numeric adjustments – now explicitly separated into Target columns.

---
## Conclusion
Iteration 3 reframes the SFMEA as a living risk register tied directly to implemented and planned technical controls. The added granularity (Local vs End Effect, pre/post scoring) enables clearer ROI evaluation and sequencing of resilience investments.

Next Review Trigger: After implementing ≥70% of Quick Wins or after any production incident affecting data integrity or availability.