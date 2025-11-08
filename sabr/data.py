import numpy as np
import pandas as pd

def generate_synthetic_surface(expiries, forwards, params_by_T, noise=0.01):
    from .model import SABRModel
    rows = []
    for T, F in zip(expiries, forwards):
        k_grid = np.linspace(0.5*max(F,1e-4), 1.5*max(F,1e-4), 11)
        for K in k_grid:
            vol = SABRModel.hagan_implied_vol(F, K, T, params_by_T[T])
            rows.append(dict(expiry=T, forward=F, strike=K, vol=max(1e-6, vol + np.random.normal(0, noise))))
    return pd.DataFrame(rows)

def read_market_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if not ({'expiry','forward','strike'} <= set(df.columns)):
        raise ValueError("CSV must contain at least columns: expiry, forward, strike, and one of {vol, price}.")
    if ('vol' not in df.columns) and ('price' not in df.columns):
        raise ValueError("CSV must have 'vol' or 'price'.")
    return df
