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
