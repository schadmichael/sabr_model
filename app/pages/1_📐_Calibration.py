import streamlit as st
import numpy as np
import pandas as pd
from sabr.curves import FlatCurve
from sabr.calibration import SABRCalibrator
from sabr.model import SABRParams, SABRModel
from sabr.plotting import smile_figure
from sabr.black import black_price
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

st.title("Calibration SABR")

with st.sidebar:
    beta = st.slider("β (fixe)", 0.0, 1.0, 0.5, 0.1)
    mode = st.radio("Calibration sur", ["Volatilités", "Prix"], index=0)
    noise = st.slider("Bruit synthétique (si génération)", 0.0, 0.05, 0.01, 0.005)

calibrator = SABRCalibrator(beta=beta)
curve = st.session_state.get("curve", FlatCurve(0.02))

data_mode = st.radio("Source des données", ["Générer", "Importer CSV"], index=0, horizontal=True)

if data_mode == "Importer CSV":
    up = st.file_uploader("CSV: expiry, forward, strike, vol (ou price)", type=["csv"])
    if up is None:
        st.stop()
    mkt = pd.read_csv(up)
else:
    expiries = np.array([1.0, 3.0, 5.0, 7.0])
    forwards = np.array([curve.forward_swap_rate(T, T+5, freq=1) for T in expiries])
    true_params = {1.0:SABRParams(0.04,beta,-0.2,0.40), 3.0:SABRParams(0.035,beta,-0.25,0.35), 5.0:SABRParams(0.03,beta,-0.2,0.30), 7.0:SABRParams(0.028,beta,-0.15,0.28)}
    rows=[]
    for T,F in zip(expiries,forwards):
        k_grid = np.linspace(0.5*max(F,1e-4), 1.5*max(F,1e-4), 11)
        for K in k_grid:
            vol = SABRModel.hagan_implied_vol(F,K,T,true_params[T])
            val = max(1e-6, vol + np.random.normal(0, noise))
            rows.append(dict(expiry=T, forward=F, strike=K, vol=val))
    mkt = pd.DataFrame(rows)

st.dataframe(mkt.head(), use_container_width=True)

calib_rows = []
# Liste des maturités disponibles
all_T = sorted(mkt['expiry'].unique())
T_choices = st.multiselect(
    "Choisir les maturités à calibrer",
    options=all_T,
    default=all_T[0],
    help="Sélectionnez une ou plusieurs maturités à inclure dans la calibration."
)

#calib_rows = []
for T in T_choices:
#for T in sorted(mkt['expiry'].unique()):
    df_T = mkt[mkt['expiry']==T].sort_values('strike')
    F_T = float(df_T['forward'].iloc[0])
    strikes = df_T['strike'].values

    if mode == "Volatilités":
        vols = df_T['vol'].values if 'vol' in df_T.columns else None
        if vols is None:
            st.error("Pas de colonne 'vol' pour la calibration sur volatilités.")
            st.stop()
        res = calibrator.calibrate_to_vols(F_T, T, strikes, vols)
        calib_rows.append(dict(expiry=T, alpha=res.params.alpha, beta=res.params.beta, rho=res.params.rho, nu=res.params.nu, loss=res.loss))
        model_vals = np.array([SABRModel.hagan_implied_vol(F_T, k, T, res.params) for k in strikes])
        market_vals = vols
        y_label = "Vol (annuelle)"
    else:
        # Prices mode
        if 'price' in df_T.columns:
            prices = df_T['price'].values
        elif 'vol' in df_T.columns:
            # convert vols to prices for consistency
            vols = df_T['vol'].values
            df_opt = curve.df(T)
            prices = np.array([black_price(F_T, k, T, v, df_opt, call=True) for k,v in zip(strikes, vols)])
        else:
            st.error("CSV doit contenir 'price' ou 'vol'.")
            st.stop()
        df_opt = curve.df(T)
        res = calibrator.calibrate_to_prices(F_T, T, strikes, prices, df=df_opt, call=True)
        calib_rows.append(dict(expiry=T, alpha=res.params.alpha, beta=res.params.beta, rho=res.params.rho, nu=res.params.nu, loss=res.loss))
        model_vals = np.array([black_price(F_T, k, T, SABRModel.hagan_implied_vol(F_T, k, T, res.params), df_opt, call=True) for k in strikes])
        market_vals = prices
        y_label = "Prix (actualisé)"

    # Plot smile values
    fig = smile_figure(strikes, market_vals, model_vals, f"Smile — T={T} an(s)", y_label)
    st.plotly_chart(fig, use_container_width=True)

    # Exports
    exp_df = pd.DataFrame({"strike": strikes, "market": market_vals, "model": model_vals})
    st.download_button(f"T{T} — Export CSV", data=exp_df.to_csv(index=False), file_name=f"smile_T{T}.csv", mime="text/csv")
    try:
        png_bytes = fig.to_image(format="png")
        st.download_button(f"T{T} — Export PNG", data=png_bytes, file_name=f"smile_T{T}.png", mime="image/png")
    except Exception as e:
        st.info("Pour l'export PNG, installez 'kaleido'.")

calib_df = pd.DataFrame(calib_rows)
st.subheader("Paramètres calibrés")
st.dataframe(calib_df.style.format({"alpha":"{:.4f}",
                                    "rho":"{:.3f}",
                                    "nu":"{:.4f}",
                                    "loss":"{:.6f}"}),
                                     use_container_width=True)

# Save to session for other pages
st.session_state['mkt'] = mkt
st.session_state['calib'] = calib_df
