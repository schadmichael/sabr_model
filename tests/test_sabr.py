import numpy as np
from sabr.model import SABRParams, SABRModel
from sabr.black import black_price

def test_hagan_vol_atm_positive():
    F, T = 0.02, 5.0
    p = SABRParams(alpha=0.03, beta=0.5, rho=-0.2, nu=0.4)
    vol = SABRModel.hagan_implied_vol(F, F, T, p)
    assert vol > 0

def test_black_price_call_put_parity_basic():
    F, K, T, vol, df = 0.02, 0.02, 5.0, 0.25, 1.0
    c = black_price(F,K,T,vol,df,True)
    p = black_price(F,K,T,vol,df,False)
    assert abs(c - p - df*(F-K)) < 1e-8
