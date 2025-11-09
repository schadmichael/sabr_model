import streamlit as st
import numpy as np
import pandas as pd
from sabr.plotting import surface_figure
from sabr.model import SABRModel, SABRParams
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

st.title("Nappe de volatilité 3D")

if 'mkt' not in st.session_state:
    st.error("Pas de données en session. Allez sur la page Calibration d'abord.")
    st.stop()

mkt = st.session_state['mkt']

expiries_sorted = np.array(sorted(mkt['expiry'].unique()))
K_min, K_max = float(mkt['strike'].min()), float(mkt['strike'].max())
K_grid = np.linspace(K_min, K_max, 35)
Z = np.zeros((len(expiries_sorted), len(K_grid)))

# Params: if user calibrated, try to map; otherwise default
params_by_T = {}
if 'calib' in st.session_state:
    df = st.session_state['calib']
    for _,r in df.iterrows():
        params_by_T[float(r['expiry'])] = SABRParams(alpha=float(r['alpha']), beta=0.5, rho=float(r['rho']), nu=float(r['nu']))
else:
    for T in expiries_sorted:
        params_by_T[T] = SABRParams(0.035, 0.5, -0.2, 0.35)

for i,T in enumerate(expiries_sorted):
    F_T = float(mkt.loc[mkt['expiry']==T, 'forward'].iloc[0])
    p = params_by_T.get(T, SABRParams(0.035,0.5,-0.2,0.35))
    for j,K in enumerate(K_grid):
        Z[i,j] = SABRModel.hagan_implied_vol(F_T, K, T, p)

surf = surface_figure(K_grid, expiries_sorted, Z, 'Nappe de volatilité 3D')
st.plotly_chart(surf, use_container_width=True)

# Export surface CSV/PNG
surf_df = pd.DataFrame(Z, index=[f"T={t}" for t in expiries_sorted], columns=[f"K={k:.6f}" for k in K_grid])
st.download_button("Export CSV — Surface", data=surf_df.to_csv(), file_name="vol_surface.csv", mime="text/csv")
try:
    png_bytes = surf.to_image(format="png")
    st.download_button("Export PNG — Surface", data=png_bytes, file_name="vol_surface.png", mime="image/png")
except Exception as e:
    st.info("Pour l'export PNG, installez 'kaleido'.")
