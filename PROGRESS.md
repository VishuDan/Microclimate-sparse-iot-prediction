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
