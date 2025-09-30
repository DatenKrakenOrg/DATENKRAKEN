# Extended SFMEA & Comparison

This chapter augments and reflects the original SFMEA versions (project start vs. extended state). Focus: consistency, RPN evolution, remaining gaps (especially detection) and derived additional mitigations (notably alerting & data validation).

## Overview comparison
| Aspect | Initial SFMEA | Extended SFMEA | Observation |
|--------|---------------|----------------|-------------|
| Component scope | Arduino, subscription, DB (UI WIP) | UI added | Full system view achieved |
| Peak RPN | 216 (FA7) | 210 (FA2 still high, FA7 reduced) | Some mitigation effect (FA7) |
| Detection classification | Many dormant/hidden (transfer chain) | Partially evident (subscription) | No active outage notification |
| Mitigation focus | Retry, calibration, caching | Priority reductions listed | Effect only partly evidenced |

## Notable issues & plausibility
- FA2 (sensor inaccuracy) remains high → no documented calibration or drift detection.
- FA6/FA7 detection shift (Hidden→Evident) not fully justified (missing monitoring/log artefacts).
- FA7 RPN drop (216→96) seems aggressive without evidence of persistent buffering.
- Missing explicit "Arduino offline detection" mode (now added as FA13) – previously implicit across FA1/FA5.

## Added / refined failure modes
| New ID | Component | Failure Mode | Cause | Effect | Remark |
|--------|-----------|-------------|-------|--------|--------|
| FA13 | Monitoring / alerting | Data stream outage unnoticed | No heartbeat / timeout | Delayed response, data gap | Separates detection aspect of FA1/FA5 |
| FA14 | Data quality pipeline | Drift undetected | Sensor aging | Gradual incorrect insights | Adds temporal dimension to FA2 |
| FA15 | Process | Incomplete merge (missing tests/docs) | Fuzzy DoD | Introduces defects | Process risk spanning multiple modes |

## New / extended scoring (excerpt)
| ID | S | O | D | RPN | Rationale (detection focus) |
|----|---|---|---|-----|------------------------------|
| FA13 | 8 | 4 | 8 | 256 | Highest RPN – no active detection (purely reactive) |
| FA14 | 6 | 5 | 7 | 210 | Drift is hard to detect without routine |
| FA15 | 5 | 5 | 6 | 150 | Process gap drives quality fluctuation |

This shifts the critical hotspot clearly to FA13 (alerting gap) – justifying the new feature.

## Mitigation matrix (old vs. new)
| Failure Mode | Existing Control | Gap | Proposed Addition |
|--------------|------------------|-----|------------------|
| FA2 | Generic "calibration" | No interval / drift metric | Quarterly calibration + median profile plausibility |
| FA5 | ACK / retry | No sequence supervision | Sequence number + backoff + offline counter |
| FA7 | Claimed queue/buffer | No artefact evidence | Persistent replay buffer (local SQLite) |
| FA9 | Caching & reconnect | No timeout metrics | Health endpoint + Prometheus counter |
| FA13 | (—) | No timeout defined | Heartbeat interval + offline mail alert |
| FA14 | (—) | No drift metric | Rolling z‑score / IQR outlier stats |
| FA15 | (—) | DoD not enforced | Checklist gate in PR template |

## RPN reduction prognosis after alerting
| Mode | Base RPN | Measure | Expected change (D or O) | Target RPN |
|------|----------|---------|--------------------------|------------|
| FA13 | 256 | Heartbeat topic + 5‑min timeout + mail alert | D: 8→3 | 96 |
| FA5 | 192 | Sequence + retransmit | D: 6→4 | 128 |
| FA2 | 210 | Quarterly calibration + drift stats | O:6→4, D:5→4 | 112 |

## Alerting feature priority rationale
- Highest newly identified RPN (FA13)
- Low implementation complexity (timeout + email)
- Improves detection across multiple modes (FA1, FA5, FA6)
- Enables measurable MTTD metric

## Recommended quality assurance hooks
| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| MQTT ingestion | Last timestamp cache | Offline detection |
| Subscription script | Sequence validator | Loss / reordering visibility |
| DB layer | Write result counter | Early persistence failure signal |
| Frontend | Staleness badge | Transparency of data freshness |
| Process | PR checklist | DoD enforcement |

## Summary
Original SFMEA covers key data flow risks but systematically underestimates detection and process risks. Extension with FA13–FA15 sharpens prioritization. The alerting feature addresses structural blindness and shifts the risk apex. Follow‑up: drift detection (FA14) and process hardening (FA15).
