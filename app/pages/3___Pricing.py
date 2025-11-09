# app/pages/3_💵_Pricing.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import numpy as np
from sabr.curves import FlatCurve
from sabr.pricer import InterestRatePricerSABR
from sabr.model import SABRParams

st.title("Pricing: Swaption / Cap / Floor")

curve = st.session_state.get("curve", FlatCurve(0.02))
with st.sidebar:
    beta = st.slider("β", 0.0, 1.0, 0.5, 0.1, key="beta_pricing")

pricer = InterestRatePricerSABR(curve=curve, beta=beta)

# Charger les paramètres calibrés si présents
if 'calib' in st.session_state:
    df = st.session_state['calib']
    for _, r in df.iterrows():
        pricer.set_params(float(r['expiry']),
                          SABRParams(alpha=float(r['alpha']), beta=beta,
                                     rho=float(r['rho']), nu=float(r['nu'])))
else:
    for T in [1.0, 3.0, 5.0]:
        pricer.set_params(T, SABRParams(alpha=0.035, beta=beta, rho=-0.2, nu=0.35))

tabs = st.tabs(["Swaption", "Cap", "Floor"])

# ---------------- Swaption ----------------
with tabs[0]:
    notional_sw = st.number_input("Notional", 1_000.0, 1_000_000_000.0,
                                  1_000_000.0, 1000.0, key="sw_notional")
    T_sw = st.slider("Maturité option (T)", 0.5, 10.0, 5.0, 0.5, key="sw_T")
    tenor_sw = st.slider("Tenor du swap (années)", 1.0, 30.0, 5.0, 0.5, key="sw_tenor")
    F_T_sw = curve.forward_swap_rate(T_sw, T_sw + tenor_sw, freq=1)
    K_sw = st.number_input("Strike (taux fixe)", value=float(np.round(F_T_sw, 4)),
                           key="sw_strike", format="%.6f")
    payer_sw = st.radio("Type", ["Payer (call)", "Receiver (put)"],
                        index=0, key="sw_type") == "Payer (call)"
    try:
        price_sw = pricer.price_swaption(notional_sw, T_sw, tenor_sw, K_sw, payer=payer_sw)
        st.metric("Prix de la swaption", f"{price_sw:,.2f}")
    except Exception as e:
        st.error(str(e))

# ---------------- Cap ----------------
with tabs[1]:
    notional_cap = st.number_input("Notional", 1_000.0, 1_000_000_000.0,
                                   1_000_000.0, 1000.0, key="cap_notional")
    years_cap = st.slider("Maturité (années)", 1, 15, 5, key="cap_years")
    freq_cap = st.selectbox("Fréquence", [1, 2, 4], index=2, key="cap_freq")
    K_cap = st.number_input("Strike", value=0.03, step=0.0005, format="%.4f", key="cap_strike")
    maturities_cap = list(np.round(np.arange(0, years_cap + 1e-12, 1.0 / freq_cap), 8))
    price_cap = pricer.price_cap(notional_cap, K_cap, maturities_cap, freq=freq_cap)
    st.metric("Prix du cap", f"{price_cap:,.2f}")

# ---------------- Floor ----------------
with tabs[2]:
    notional_fl = st.number_input("Notional", 1_000.0, 1_000_000_000.0,
                                  1_000_000.0, 1000.0, key="fl_notional")
    years_fl = st.slider("Maturité (années)", 1, 15, 5, key="fl_years")
    freq_fl = st.selectbox("Fréquence", [1, 2, 4], index=2, key="fl_freq")
    K_fl = st.number_input("Strike", value=0.02, step=0.0005, format="%.4f", key="fl_strike")
    maturities_fl = list(np.round(np.arange(0, years_fl + 1e-12, 1.0 / freq_fl), 8))
    price_fl = pricer.price_floor(notional_fl, K_fl, maturities_fl, freq=freq_fl)
    st.metric("Prix du floor", f"{price_fl:,.2f}")
