  ## Day 1 — Aug 24
  - Repo structure set up, synopsis and sensor plan finalized
  - Built Open-Meteo grid-fetch script + GitHub Actions workflow
  - Hit and fixed a bug: Archive API rejects today's date (needs ~5-6 day lag)
  - 25-point grid data successfully pulled for campus area
## Day 2 — Aug 25
- Ran EDA notebook in Colab: 17/25 grid nodes returned data (8 failed silently, likely API timeouts — to investigate)
- No missing values, correlations physically sensible (temp vs humidity -0.92, temp vs radiation +0.85)
- Key finding: 0.3km grid spacing showed ZERO temperature variation across nodes (all identical avg 26.44°C)
- Diagnostic test confirmed cause: Open-Meteo/ERA5 has ~10-25km native resolution — two points 15km apart showed 4.3°C difference
- Decision: widen synthetic grid to 5-15km spacing for pipeline development; documented resolution limitation in synopsis
## Day 3 — Aug 26
- Built node sensor/target split, haversine distance matrix, and IDW baseline features
- Found plain IDW had a consistent ~5°C cold bias at low-elevation target node
- Diagnosed and confirmed elevation as the cause (270m gap between target and nearest sensors)
- Added lapse-rate elevation correction: MAE improved from 5.38°C to 3.92°C
- Added cyclical time features (hour, day-of-year)
- Saved feature table to data/processed/features.csv, noted residual ~2-3°C gap for future investigation
## Day 4 — Sep 9
- Ran leave-node-out CV (GroupKFold) comparing plain IDW, elevation-corrected IDW, GPR, and Random Forest on 49-node grid
- GPR initially exploded (MAE up to 677°C) due to unbounded kernel hyperparameters extrapolating badly on constant per-node features
- Fixed via ARD kernel with explicit bounds + increased alpha; also found and fixed a stale-results bug from not resetting the results dict between runs
- Final results: Elevation-corrected IDW 3.92°C < Plain IDW 4.41°C < GPR 4.84°C < Random Forest 7.00°C
- Conclusion: physically-informed baseline beats general ML here due to limited elevation diversity (223-287m) across only 8 held-out target nodes
## Day 5 — Sep 14
- Built per-node LSTM for 1-hour-ahead temperature forecasting (24-hour lookback)
- node_0_0: naive MAE 0.60°C vs LSTM MAE 0.49°C (18% improvement), stable training
- Validated naive baseline consistency across 6 more nodes (0.50-0.79°C range) to confirm generalization
- Identified known issue: ~29% of grid nodes failed to fetch (14/49) — retry logic needed in fetch script
- Contrast with Day 4: temporal modeling gave a clean, reliable win; spatial modeling did not
## Day 6 — Sep 17
- Fixed fetch script reliability: retry-with-backoff, coverage improved 35/49 → 47/49 nodes
- Re-ran Day 3/4 pipeline on fuller 47-node dataset (11 target nodes, 11-fold leave-one-out CV)
- Fixed a hardcoded-value bug from Day 5 (elevation-corrected IDW chart was showing stale 3.92°C instead of live data)
- Real trustworthy results: Plain IDW 5.87°C < GPR 6.34°C < Elevation-corrected IDW 6.38°C < Random Forest 7.51°C
- Key finding: fixed global lapse-rate correction, which helped substantially on the small 8-node sample, does NOT generalize cleanly across more topographically diverse nodes — motivates a per-node/learned correction rather than one constant
