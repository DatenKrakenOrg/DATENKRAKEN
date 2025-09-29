# 5. Checklisten & Definition of Done

Dieses Kapitel operationalisiert Qualitätsanforderungen in Form von Checklisten

## 5.1 Analyse-Abdeckung
| Punkt | Ziel | Status |
|-------|------|--------|
| Ist-/Schwachstellenanalyse vorhanden | Dokument `01_ist_schwachstellenanalyse.md` | OK |
| Erweiterte SFMEA mit neuen Failure Modes | `02_sfmea_analyse.md` (FA13–FA15) | OK |
| Priorisierung & Begründung der 3 Optimierungen | `03_optimierungen.md` | OK |
| Neues Feature spezifiziert (Alerting) | `04_alerting_feature.md` (Ist vs Ziel) | OK |

## 5.2 Optimierung 1: Mock-Daten
| Nachweis | Zielkriterium | Status |
|----------|--------------|--------|
| `03a_mock_daten.md` | Ist vs. Ziel klar getrennt | OK |
| `fill_dummy.sql` aktualisiert | Generiert konsistentes Schema | OK |
| Keine Überclaimings (Generator, Automation) | Nur Empfehlung als Future | OK |

## 5.3 Optimierung 2: Deployment / Compose
| Nachweis | Zielkriterium | Status |
|----------|--------------|--------|
| `03b_deployment_compose.md` | Vereinheitlichung beschrieben | OK |
| Beispiel `.env` / `example.env` vorhanden | Reproduzierbar | OK |
| Alerting-Env Variablen dokumentiert | Threshold & SMTP klar | OK |

## 5.4 Optimierung 3: Frontend Error Handling
| Nachweis | Zielkriterium | Status |
|----------|--------------|--------|
| `03c_frontend_error_handling.md` | Implementiert vs. offen getrennt | OK |
| Code Fallbacks (leere Resultate) | `engine.py` / `utils.py` | OK |
| Staleness Funktion dokumentiert | `currentness.py` referenziert | OK |

## 5.5 Neues Feature: Alerting (Arduino Offline)
| Nachweis | Zielkriterium | Status |
|----------|--------------|--------|
| Realzustand beschrieben | Inactivity + Sequenz E-Mail | OK |
| Abgrenzung Zielbild | Persistenz & UI markiert Future | OK |
| SFMEA Rückwirkung erläutert | RPN-Tabelle angepasst | OK |
| Env Variablen im Code genutzt | `alerting.py` / `main.py` | OK |

## 5.6 Integrität & Nachvollziehbarkeit
| Punkt | Ziel | Status |
|-------|------|--------|
| Keine unbelegten Implementierungsbehauptungen | Dokumente decken Code | OK |
| Future klar als Future gekennzeichnet | Keine Vermischung | OK |
| Alle neuen Dateien datiert | Platzhalter entfernt | OK |

## 5.7 Minimale Definition of Done (für diese Abgabe)
Ein Beitrag (Dok/Code) gilt als fertig, wenn:
1. Relevantes Dokument aktualisiert oder neu angelegt (siehe 5.1–5.5).
2. Keine falschen Ist-Behauptungen (nur verifizierter Code referenziert).
3. Future-Anteile klar markiert ("Future", "Ziel", "nicht implementiert").
4. Env / Konfig Abhängigkeiten dokumentiert (falls betroffen).
5. Querreferenzen (Dateinamen) stimmen.

## 5.8 Offene Verbesserungs-Potenziale (Nicht Abgaberelevant)
- Automatisierte Tests für Sequenz-Gaps & Offline Simulation
- Schema-Diff Skript / Latenz-Messung
- Persistente Alerting-State Machine & UI Badges
- Erweiterte Accessibility-Prüfung