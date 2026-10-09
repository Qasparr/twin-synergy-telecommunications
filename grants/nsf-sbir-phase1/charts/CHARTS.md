# Charts — NSF SBIR Phase I, Twin Synergy Telecommunications

Round-2 simulation charts (300 dpi PNG, gold #d4af37 / indigo #150826, white backgrounds).
Built from `sim_data_round2.json` by `/tmp/build_charts.py` (matplotlib 3.6.3).

Honesty note: every chart carries the caption *"Agent-based simulation, n=300 agents,
3 seeds (418/777/93), 200 rounds — preliminary data, not field measurements."*
These are simulation outputs, not field measurements.

| File | What it shows |
|---|---|
| `a_threshold_metrics_grouped.png` | Grouped bars of the six thresholded metrics ($PP legitimacy, fraud block rate, honest block rate, $00 oversupply, sybil recall, miner watch) across all seven scenarios, with dashed per-metric threshold lines and ±std error bars. |
| `b_round1_vs_round2.png` | Round-1 (pre-amendment) vs round-2 (amended) side-by-side bars for the four repaired breaks: honest block rate 0.18→0.0273 (baseline), fraud block on boosters 0.02→1, smurf block 0.62→1, combined $PP legitimacy 0.94→1. |
| `c_zero_oversupply_cap.png` | $00 oversupply per scenario against the dashed 1.10 cap; all scenarios hold, minimum headroom 0.092. |
| `d_integrity_recall.png` | Ledger integrity recall = 1.0 in every scenario and seed — no integrity failures observed on any run. |
| `e_verdict_heatmap.png` | Verdict heatmap, 7 scenarios × 6 metrics: all green, HOLD — 42/42 thresholds held in round 2. |
