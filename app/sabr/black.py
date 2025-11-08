from math import erf, sqrt, log
import numpy as np

def norm_cdf(x):
    x = np.asarray(x)
    return 0.5 * (1.0 + np.vectorize(erf)(x / sqrt(2.0)))

def black_price(F: float, K: float, T: float, vol: float, df: float, call: bool = True) -> float:
    if T <= 0 or vol <= 0:
        intrinsic = max((F - K) if call else (K - F), 0.0)
        return df * intrinsic
    if F <= 0 or K <= 0:
        return 0.0
    sigma_sqrtT = vol * sqrt(T)
    d1 = (log(F / K) + 0.5 * sigma_sqrtT**2) / sigma_sqrtT
    d2 = d1 - sigma_sqrtT
    if call:
        return df * (F * norm_cdf(d1) - K * norm_cdf(d2))
    return df * (K * norm_cdf(-d2) - F * norm_cdf(-d1))
