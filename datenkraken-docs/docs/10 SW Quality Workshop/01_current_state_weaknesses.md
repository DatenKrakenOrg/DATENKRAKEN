# Current State & Weakness Analysis

Goal: Provide a structured snapshot of product & process quality, highlight gaps against ISO/IEC 25010 and internal quality goals, and form a prioritized baseline for improvements.

## Reference Frameworks
- ISO/IEC 25010 (Product quality & Quality in use)
- Internal quality goals (arc42 “Introduction and Goals”)
- SFMEA (initial & extended) as risk driver
- Deployment & operational artifacts (Docker, monitoring, backup)
- Delivery process (Definition of Done, tests, boards)

## Evaluated ISO 25010 Characteristics (selection & relevance)
| ISO 25010 Attribute | Rationale | Current Maturity | Primary Evidence |
|---------------------|-----------|------------------|------------------|
| Functional Suitability | Correct acquisition & presentation of room climate data | Medium | Functional req. FR.1.x, UI pages |
| Reliability (Availability, Fault Tolerance) | Pipeline must tolerate short outages | Low–Medium (manual aspects) | Missing active alerting, simple retry patterns |
| Performance Efficiency | Data should reach gold layer in <5 min | Medium | NFR.1.1, no E2E latency metric captured |
| Compatibility | Components integrate via MQTT / DB | High (simple coupling) | Clear interfaces (topics, tables) |
| Usability (Accessibility) | Keyboard‑free operation (NFR.3.1) | Partial (rudimentary tests) | `frontend/tests/accessibility/test_accessibility.py` (limited) |
| Security | Sensor data + internal infra | Basic measures, no hardening doc | Missing threat model / auth layer |
| Maintainability | Change & test effort | Medium (modular, naming inconsistencies) | Mixed naming, some missing tests |
| Portability (Deployability) | Rapid environment setup | Improved (unified compose planned) | Previously multiple separate compose files |

## Internal Quality Goals vs. Reality
| Quality Goal (arc42) | Linked Failure Modes (SFMEA) | Current State | Gap |
|----------------------|-----------------------------|--------------|-----|
| Data Quality (NFR.1.1) | FA7, FA9, FA5, FA6, FA12 | Partially addressed, no end‑to‑end lead time tracking | Missing measurability |
| DB Availability 95% (NFR.1.2) | FA9, FA12 | Uptime script exists, no escalation | No alerting / trend report |
| Accessibility (NFR.3.1) | (None) | Not evidenced | Missing verification & test cases |

## Artifact Consistency (Board / Docs / Code)
| Aspect | Observation | Risk |
|--------|-------------|------|
| SFMEA → corrective actions | Not always referenced in commits | Erosion of traceability |
| Backup concept | Restore path undocumented | False sense of safety |
| Mock data | Outdated vs. schema | Misleading test assumptions |
| Frontend error handling | Now systematic (panels, fallbacks) | Previously white screen / raw trace |
| Deployment | Manual multi‑step | Onboarding latency, human error |
| Definition of Done | Unclear / not enforced | Quality variance per story |

## Key Weakness Shortlist
1. Missing active alerting (Arduino offline / data flow stall)
2. Outdated mock data → inconsistent test runs
3. No documented restore procedure (despite backup script)
4. Incomplete process definition (DoD not institutionalized)
5. No end‑to‑end data latency metric (Sensor → Gold layer)
6. Limited Arduino test coverage (edge/error cases)
7. Insufficient accessibility verification (NFR.3.1)

## Detailed Weakness Analysis
### Alerting gap
- Symptom: No active notification when MQTT messages stop.
- Effect: Delayed detection → risk of prolonged data gaps.
- Reference: SFMEA FA1, FA5, FA6 (detection often dormant/hidden).
- Impact: High (prevents proactive response), Effort: Medium.

### Inconsistent mock data
- Symptom: Test data does not reflect schema evolution.
- Effect: Wrong UI assumptions, skewed performance perception.
- Impact: Medium, Effort: Low–Medium.

### Missing restore documentation
- Symptom: Only backup path covered.
- Effect: Backups potentially unusable (“restore gap”).
- Impact: Medium (longer recovery), Effort: Low.

### Fuzzy Definition of Done
- Symptom: No consistent quality gate.
- Effect: Variable merge quality, reduced traceability.
- Impact: Medium, Effort: Low.

### Missing latency metric
- Symptom: No measurement from send timestamp to gold availability.
- Effect: NFR.1.1 unverifiable.
- Impact: High (audit), Effort: Medium.

### Arduino test coverage
- Symptom: Edge / error cases missing.
- Effect: Possible silent failures.
- Impact: Medium, Effort: Medium–High.

### Accessibility validation
- Symptom: Only rudimentary test (absence of input widgets); no comprehensive audit (focus order, ARIA, contrast).
- Evidence: `frontend/tests/accessibility/test_accessibility.py` scope is limited.
- Effect: NFR.3.1 only partially supported; hidden barriers possible.
- Impact: Low–Medium (dashboard complexity limited), Effort: Medium (automatable + manual checklist).
- Improvement ideas:
  - Add automated axe-core / Pa11y checks via Playwright
  - Manual heuristic checklist (contrast, focus indicator, semantics)
  - Clarify explicitly optional vs. required keyboard interaction.

## Prioritized optimization focus areas
| ID | Topic | Selection Rationale | In current scope? |
|----|-------|---------------------|------------------|
| A1 | Mock data update | Fast quality lever, reduces misinterpretation | Yes |
| A2 | Docker compose deployment | Boosts reproducibility & onboarding | Yes |
| A3 | Frontend error handling | Immediate UX / resilience uplift | Yes |
| A4 | Arduino offline alerting | Critical missing detection | Yes (new feature) |
| A5 | Restore documentation | Important but secondary | Later |
| A6 | DoD sharpening | Process quality iteration | Later |
| A7 | Latency metric | Higher technical effort | Later |

## Metric proposals
| Goal | Proposed Metric | Capture Method |
|------|-----------------|----------------|
| Data latency | P95 end‑to‑end (Arduino ts → gold row ts) | Log correlation + Timescale query |
| DB availability | % minutes health check passes | Uptime script aggregation |
| UI fault robustness | # uncaught exceptions / session | Logging + test harness |
| Mock data quality | Schema diff count = 0 | Automated schema vs. sample diff |
| Deployment reproducibility | Onboarding time → first dashboard | Self report + timer |
| Alerting effectiveness | Mean Time To Detect (MTTD) | Simulated outage timestamp diff |

## Summary
Base functionality & modular structure are solid. Largest gaps: (1) missing active monitoring (alerting), (2) representative / validated mock data, (3) unified deployment & consistent UI resilience. Selected optimizations directly improve risk reduction, transparency and perceived quality.
