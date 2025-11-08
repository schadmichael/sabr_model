import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from sabr.curves import FlatCurve, ZeroCurve
import plotly.express as px

st.title("Courbe de taux")

# -----------------------------------------------------
# 📁 Fichier de courbe par défaut
# -----------------------------------------------------
DEFAULT_CURVE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sample_curve.csv")
)

# -----------------------------------------------------
# 🔄 Chargement automatique de la courbe par défaut
# -----------------------------------------------------
if "curve" not in st.session_state:
    if os.path.exists(DEFAULT_CURVE_PATH):
        df_default = pd.read_csv(DEFAULT_CURVE_PATH)
        st.session_state["curve"] = ZeroCurve(
            df_default["maturity"].values, df_default["zero_rate"].values
        )
        st.info(f"✅ Courbe par défaut chargée ({len(df_default)} points)")
    else:
        st.session_state["curve"] = FlatCurve(rate=0.02)
        st.warning("⚠️ Fichier de courbe par défaut introuvable, utilisation d'une courbe plate (2%).")

# -----------------------------------------------------
# 📤 Option : uploader une autre courbe
# -----------------------------------------------------
st.subheader("Charger une nouvelle courbe de taux")
uploaded_file = st.file_uploader(
    "Importer un CSV contenant `maturity, zero_rate`",
    type=["csv"],
    help="Colonnes requises : maturité en années, taux zéro en continu."
)

if uploaded_file is not None:
    try:
        df_new = pd.read_csv(uploaded_file)
        if not {"maturity", "zero_rate"} <= set(df_new.columns):
            st.error("❌ Le CSV doit contenir les colonnes `maturity` et `zero_rate`.")
        else:
            st.session_state["curve"] = ZeroCurve(
                df_new["maturity"].values, df_new["zero_rate"].values
            )
            st.success(f"✅ Nouvelle courbe chargée ({len(df_new)} points).")
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")

# -----------------------------------------------------
# 🧠 Affichage de la courbe actuelle
# -----------------------------------------------------
curve = st.session_state["curve"]

# Si c’est une courbe ZeroCurve, on affiche les points
if isinstance(curve, ZeroCurve):
    maturities = st.slider("Afficher jusqu’à quelle maturité (ans)", 0.5, 30.0, 10.0, 0.5)
    grid = pd.DataFrame({
        "Maturity (ans)": [t for t in [x/2 for x in range(1, int(maturities*2)+1)]],
    })
    grid["Zero rate"] = [curve.zero(t) for t in grid["Maturity (ans)"]]
    grid["Discount factor"] = [curve.df(t) for t in grid["Maturity (ans)"]]
    fig = px.line(grid, x="Maturity (ans)", y="Zero rate", title="Courbe de taux zéro")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(grid, use_container_width=True)
else:
    st.info("Courbe plate utilisée.")
    st.write(f"Taux sans risque constant : {curve.rate:.4%}")
