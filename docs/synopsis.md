# Project Synopsis

## Title
**Hyperlocal Microclimate Prediction Using a Sparse IoT Sensor Network**

## Problem Statement
Standard weather forecasts operate at a coarse spatial resolution (several kilometers), which fails to capture significant microclimatic variation across small, heterogeneous areas such as a farm or a college campus — differences caused by tree canopy, building shadows, soil type, water bodies, and elevation changes. This project builds a machine learning pipeline that predicts hyperlocal temperature, humidity, soil moisture, and light intensity at unmonitored locations within a small geographic area, using data from a sparse network of low-cost IoT sensor nodes.

## Objectives
1. Deploy a small (4-6 node) sparse IoT sensor network across a defined campus/farm area.
2. Collect and clean time-series environmental data from each node.
3. Build spatial interpolation models to estimate conditions at unmonitored points.
4. Build temporal forecasting models to predict short-term future readings at each node.
5. Combine both into a spatiotemporal prediction pipeline and evaluate how prediction accuracy degrades as sensor density decreases.
6. Visualize predictions as an interactive microclimate map.

## Hardware / Sensors Used
| Component | Purpose |
|---|---|
| ESP32 microcontroller (x4-6) | WiFi-enabled data acquisition per node |
| DHT22 | Temperature and humidity sensing |
| Capacitive soil moisture sensor v1.2 | Soil moisture sensing |
| BH1750 | Ambient light intensity (lux) |
| BMP280 *(optional)* | Air pressure / elevation correction |

Nodes are placed at microclimatically distinct points (e.g., open field, under canopy, near a building, near water) rather than a uniform grid, to maximize spatial contrast for the interpolation task. Each node pushes readings every 5-15 minutes to a cloud logging endpoint (ThingSpeak / Google Sheets webhook).

## Dataset
**Primary (real):** Sensor readings collected from the deployed ESP32 network over the project duration (target: minimum 7-10 days of continuous logging).

**Secondary (simulation/backup):** Historical hourly weather data pulled via the **Open-Meteo API** for the campus/farm's bounding box, used to (a) bootstrap and validate the pipeline before hardware deployment is complete, and (b) create a larger synthetic "sparse network" by subsampling grid points as pseudo-sensors and holding out others as ground truth — a standard technique for testing spatial interpolation methods when real deployment is limited.

## Data Resolution Limitation (discovered Day 2)

Exploratory analysis of the Open-Meteo Archive API data revealed that it is backed by a reanalysis model (ERA5) with a native spatial resolution on the order of several kilometers. A diagnostic test confirmed this directly: two points ~15km apart showed a 4.3°C difference in average temperature over the same period, while a 5×5 grid spaced only 0.3km apart returned identical average values across all points (26.44°C, zero variation).

This means the Open-Meteo dataset can validate the modeling pipeline (interpolation, forecasting, evaluation harness) but cannot itself demonstrate sub-kilometer "hyperlocal" microclimate variation — it structurally lacks the resolution to see effects like canopy shade, building shadowing, or localized soil moisture differences. This is precisely the gap the physical ESP32 sensor network is designed to fill: sensors placed a few hundred meters apart across genuinely different microclimate zones (open field, under canopy, near a wall, near water) can capture real variation that no reanalysis product resolves.

Practical implication: for pipeline development and testing, the synthetic grid is now spaced 5-15km apart (rather than 0.3km) to generate non-degenerate spatial data. The tighter 0.3km hyperlocal claim is reserved for, and validated against, the real physical sensor deployment.
## Methodology
1. **Data pipeline:** Ingest sensor + API data, clean, timestamp-align, handle missing values.
2. **Spatial interpolation baselines:** Inverse Distance Weighting → Gaussian Process Regression / Kriging → Random Forest with distance/elevation features.
3. **Temporal forecasting:** Per-node short-horizon forecasting (ARIMA baseline → LSTM).
4. **Spatiotemporal fusion:** Combine spatial and temporal models to predict future conditions at unmonitored locations.
5. **Robustness analysis:** Evaluate how RMSE/MAE changes as the number of "active" sensors is reduced (simulating sparser deployments).
6. **Visualization:** Interactive heatmap of predicted microclimate variables across the campus/farm using Folium/Plotly.

## Tools & Stack
Python, scikit-learn, PyTorch/statsmodels, pandas, Folium/Plotly, ESP32/Arduino IDE, ThingSpeak/Google Sheets API, GitHub for version control and daily progress tracking.

## Timeline
2-3 weeks — Week 1: data pipeline + spatial baselines. Week 2: temporal + spatiotemporal models, sensitivity analysis. Week 3: visualization, documentation, polish.

## Expected Outcome
A working, documented pipeline that predicts hyperlocal environmental conditions at unmonitored points within a small area, along with an empirical analysis of how sensor sparsity affects prediction accuracy, and an interactive visualization of the predicted microclimate map.
