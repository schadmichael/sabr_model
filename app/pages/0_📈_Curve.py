import streamlit as st
import pandas as pd
from sabr.curves import FlatCurve, ZeroCurve
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

st.title("Courbe de taux")

st.markdown("Chargez une **courbe zéro** (maturité en années, taux zéro en continu) ou utilisez une courbe **plate**.")

tab1, tab2 = st.tabs(["Importer courbe (CSV)", "Courbe plate"])

with tab1:
    up = st.file_uploader("CSV avec colonnes: maturity, zero_rate", type=["csv"])
    if up is not None:
        df = pd.read_csv(up)
        if not {"maturity","zero_rate"} <= set(df.columns):
            st.error("Le CSV doit contenir les colonnes: maturity, zero_rate")
        else:
            curve = ZeroCurve(df["maturity"].values, df["zero_rate"].values)
            st.session_state["curve"] = curve
            st.success(f"Courbe zéro chargée ({len(df)} points).")

with tab2:
    r = st.slider("Taux sans risque (continu)", -0.01, 0.08, 0.02, 0.001)
    if st.button("Utiliser cette courbe plate"):
        st.session_state["curve"] = FlatCurve(rate=r)
        st.success(f"Courbe plate fixée à r={r:.4f}.")
