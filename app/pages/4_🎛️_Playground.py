import streamlit as st
import numpy as np
from sabr.curves import FlatCurve
from sabr.model import SABRParams, SABRModel
import plotly.graph_objs as go
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

st.title("Playground SABR")

curve = st.session_state.get("curve", FlatCurve(0.02))


c1, c2, c3 = st.columns(3)
T_min = c1.number_input("Maturité min", 0.25, 50.0, 1.0, 0.25)
T_max = c2.number_input("Maturité max", 0.5, 60.0, 7.0, 0.5)
n_T    = c3.slider("# maturités", 3, 40, 10)
expiries = np.linspace(T_min, T_max, n_T)

tenor = st.slider("Tenor du swap pour F(T)", 1.0, 30.0, 5.0, 0.5)
F_vec = np.array([curve.forward_swap_rate(T, T+tenor, freq=1) for T in expiries])

rel_min, rel_max = st.slider("Plage strikes/F", 0.5, 1.5, (0.7, 1.3), 0.01)
n_K = st.slider("# strikes", 5, 80, 35)

colA, colB, colC, colD = st.columns(4)
alpha_pg = colA.slider("α", 0.0001, 0.20, 0.0400, 0.0001)
beta_pg  = colB.slider("β", 0.0, 1.0, 0.5, 0.05)
rho_pg   = colC.slider("ρ", -0.99, 0.99, -0.20, 0.01)
nu_pg    = colD.slider("ν", 0.0001, 2.0, 0.40, 0.01)


K_grid = []
Z = np.zeros((len(expiries), n_K))
for i, (T, F_T) in enumerate(zip(expiries, F_vec)):
    K_row = np.linspace(max(1e-6, rel_min*max(F_T,1e-6)), max(1e-6, rel_max*max(F_T,1e-6)), n_K)
    K_grid.append(K_row)
    p = SABRParams(alpha=alpha_pg, beta=beta_pg, rho=rho_pg, nu=nu_pg)
    Z[i, :] = [SABRModel.hagan_implied_vol(F_T, k, T, p) for k in K_row]

# Align to a common strike grid for surface
K_min = min(row[0] for row in K_grid)
K_max = max(row[-1] for row in K_grid)
K_common = np.linspace(K_min, K_max, n_K)
Zc = np.zeros_like(Z)
for i in range(len(expiries)):
    Zc[i,:] = np.interp(K_common, K_grid[i], Z[i,:])

surf = go.Figure(data=[go.Surface(x=K_common, y=expiries, z=Zc)])
surf.update_layout(scene=dict(xaxis_title='Strike', yaxis_title='Maturité (ans)', zaxis_title='Vol (annuelle)'),
                   title='Nappe de volatilité — Playground', template='plotly_dark', height=550)
st.plotly_chart(surf, use_container_width=True)

# ATM vs T
atm = []
for T, F_T in zip(expiries, F_vec):
    p = SABRParams(alpha=alpha_pg, beta=beta_pg, rho=rho_pg, nu=nu_pg)
    atm.append(SABRModel.hagan_implied_vol(F_T, F_T, T, p))
fig_atm = go.Figure()
fig_atm.add_trace(go.Scatter(x=expiries, y=atm, mode='lines+markers', name='Vol ATM'))
fig_atm.update_layout(title='Volatilité ATM vs maturité', xaxis_title='Maturité (ans)', yaxis_title='Vol', template='plotly_dark')
st.plotly_chart(fig_atm, use_container_width=True)
