# SABR Pricer 

Modular SABR pricing toolkit with a multi-page Streamlit app:
- Calibrate SABR (α, ρ, ν) with fixed β — now from **vols or prices**
- Visualize smiles and **3D vol surface**
- Price **Swaptions, Caps, Floors** (Black + SABR)
- Load a **real curve** from CSV (zero rates) or use a flat curve
- **Export** CSV/PNG of smiles and surfaces

## Quickstart
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Data
- Market CSV with columns: `expiry,forward,strike,vol` (or `price` if calibrating to prices)
- Curve CSV with columns: `maturity,zero_rate` (continuous comp, annual)

## Tests
```bash
pytest
```
