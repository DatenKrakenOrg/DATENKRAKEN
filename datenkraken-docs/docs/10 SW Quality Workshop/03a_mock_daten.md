# 3a. Optimierung: Mock-Daten Aktualisierung

## Ausgangslage (Realer Zustand)
Es existiert ein manuell auszuführendes SQL Skript `database/utils/fill_dummy.sql`, das mit Hilfe von `generate_series` Zufalls-/synthetische Messwerte (noise, temperature, humidity, voc) für ca. 60 Tage erzeugt und in die Bronze-Tabellen schreibt.

Historie:
- Das Skript war veraltet (Ziel: Menge / Struktur passte nicht mehr vollständig zum gewünschten Datenbild) und wurde aktualisiert (Felder & Verteilungen angepasst).
- Es gibt KEIN automatisiertes Generierungs- oder Validierungsskript (z.B. kein Python Generator, kein Schema-Diff Check) – Ausführung erfolgt ad hoc nach Bedarf.

Aktueller Umfang des Skripts:
| Tabelle | Generierungslogik | Frequenz | IDs verteilt |
|---------|-------------------|----------|--------------|
| bronze.noise | Zufallswerte (0–1028) | 1 Minute (2 Offsets) über 60 Tage | 401/402/403 (n basierend) |
| bronze.temperature | Zufallswert 5–30 | alle 30 Sekunden | Round-Robin 401–403 |
| bronze.humidity | Zufallswert 5–30 | alle 30 Sekunden | Round-Robin 401–403 |
| bronze.voc | Zufallswert 5–30 | alle 30 Sekunden | Round-Robin 401–403 |

Limitationen Realzustand:
- Keine semantischen Muster (Tag/Nacht, Peaks bei Fensterschließung, etc.)
- Kein Abgleich gegen echtes Schema vor Insert (Annahme: Tabellen existieren)
- Keine einfache Parametrisierung (z.B. Dauer / Anzahl Geräte variable)
- Keine Trennung zwischen Development vs. Test Datensätzen

## Ziele (perspektivisch – noch nicht umgesetzt)
| Ziel | Beschreibung | Vorschlag Messkriterium |
|------|--------------|-------------------------|
| Schema-Konformität | Automatischer Abgleich Spaltennamen/Datentypen | 0 Schema-Diffs / Lauf |
| Muster-Realismus | Simulierte Tag/Nacht & Ausreißer | Qualitative Review / definierte Varianz |
| Reproduzierbarkeit | Parametrisierte Generatoren mit Seed | Fester Seed liefert gleiche Statistik |
| Automatisierbarkeit | CI Job kann Daten erzeugen | Erfolgreicher Pipeline-Run |

## Empfohlene zukünftige Maßnahmen (nicht umgesetzt – Empfehlung)
1. Python Generator (`/tools/mockgen/`) mit Parametern: `--rooms`, `--duration-days`, `--pattern day-night|flat`, `--seed`.
2. Schema-Introspektion gegen `information_schema.columns` → Warnung bei Drift.
3. Erweiterte Muster (Sinus Temperatur, CO2 Peaks, Feuchte Drift, Geräusch-Spikes).
4. Validierung: Typ-Konsistenz + minimale/Max Werte, sonst Abbruch.
5. Optional: Nightly CI Job generiert kleine Stichprobe + Diff Report.

## Risiken & Mitigation (Ist vs. Empfehlung)
| Risiko | Aktueller Zustand | Mitigation (Empfehlung) |
|--------|------------------|-------------------------|
| Schema Drift | Manuelles Auffallen beim Insert | Automatischer Diff Check |
| Unrealistische Verteilung | Reine Zufallswerte | Gemusterte Generatoren |
| Nicht-Reproduzierbarkeit | Jede Ausführung anders | Seed-Steuerung |
| Datenexplosion | Hoher Umfang (60 Tage) | Parametrisierung Dauer |

## Erweiterungen (Future)
- Sampling realer Produktionsdaten (anonymisiert) + Hybrid Mock.
- Statistische Distribution-Checks (KS-Test gegen Referenzset).
- Outlier-Injection Flags für Negativtests.

## Nachweis (bisherige Änderung)
| Aspekt | Vorher | Jetzt |
|--------|--------|------|
| Skript Aktualität | Veraltet | Aktualisiert (läuft gegen aktuelles Schema) |
| Automatisierung | Keine | Unverändert (keine Automatisierung) |
| Realismus Muster | Einfacher Zufall | Unverändert |
| Parametrisierung | Keine | Unverändert |

## Potenzieller Nutzen zukünftiger Umsetzung
| Ziel | Erwarteter Mehrwert |
|------|--------------------|
| Validierungs-Checks | Frühe Drift-Erkennung |
| Realistische Muster | Validere Performance- & UI Verhaltenstests |
| Reproduzierbarkeit | Vergleichbarkeit Builds |
| Parametrisierte Dauer | Schnellere lokale Testsets |
