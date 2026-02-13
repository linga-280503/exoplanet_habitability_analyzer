# 🧪 Exoplanet Habitability Analyzer (Python + Streamlit + MongoDB)

A ready‑to‑run **Exoplanet Habitability Analyzer** with a **dark / fantasy planetary galaxy UI**. 
Analyze CSV datasets or seed demo planets, compute **habitable‑zone flux**, **equilibrium temperature**, and an overall **habitability score (0–100)**, then save, filter, chart, and favorite results — all backed by **MongoDB**.

> **Habitable‑zone (HZ) math** follows the **Kopparapu et al.** parameterization: conservative inner edge = **Moist Greenhouse**, outer edge = **Maximum Greenhouse**. Coefficients and usage notes available in Kopparapu (2013/2014) and associated tools. citeturn7search65turn7search66turn7search68turn7search69
>
> Column definitions for NASA **Exoplanet Archive** tables (if you later add a live downloader) are documented here. citeturn7search61turn7search63turn7search55

## ✨ Features
- **CSV ingest** (drag/drop) with smart unit inference (Earth radii, AU, K, solar units)
- **Demo data** (Earth, TRAPPIST‑1 e, Kepler‑452 b, Proxima Centauri b)
- **Kopparapu HZ bounds** → per‑star inner/outer flux; compares planet **insolation flux**
- **Scoring** (0–100): flux proximity, size, eccentricity, stellar type, equilibrium temperature, metallicity
- **Explore**: tables + filters + Plotly charts (Flux vs Radius, Teq vs Radius, Score histogram)
- **Details view**: planet card, badges, and a polar gauge for score
- **Favorites & notes** stored in MongoDB

## 🚀 Quickstart

### 1) MongoDB
- Local default: `mongodb://localhost:27017`
- Atlas: paste your connection string

### 2) Install
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
. .venv/bin/activate
pip install -r requirements.txt
```

### 3) Run
```bash
streamlit run src/app.py
```

### 4) In the app
- Enter **Mongo URI** & **DB name** → **Connect**
- **Seed Demo Data** or **Upload CSV** → **Analyze**

## 📦 Data format (CSV)
Minimal columns (case‑insensitive):
- `name` (string)
- `pl_rade` (planet radius in Earth radii) **or** `pl_radj` (Jupiter radii)
- `pl_orbsmax` (semi‑major axis in AU) **or** `pl_orbper` (days) + `st_mass` (Msun)
- `st_teff` (K)
- **Optional**: `st_rad` (Rsun), `st_lum` (Lsun), `pl_orbeccen`, `st_metfe` (dex), `st_spectype` (e.g., G2V), `ra`, `dec`

> If `st_lum` is missing, the app estimates luminosity via **R²·(T/5772)^4**; if `a` is missing, it estimates via Kepler’s law using `P` and `M⋆`. (Fields and units consistent with Exoplanet Archive docs.) citeturn7search61

## 📚 References
- Kopparapu et al. 2013/2014 HZ parameterization and online calculators. citeturn7search65turn7search66turn7search68
- Example HZ coefficients file used by community calculators. citeturn7search69
- NASA Exoplanet Archive programmatic access & columns. citeturn7search55turn7search61turn7search63

## 📝 License
MIT
