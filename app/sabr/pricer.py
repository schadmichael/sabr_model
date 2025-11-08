import numpy as np
from typing import List, Dict
from .curves import FlatCurve, ZeroCurve
from .black import black_price
from .model import SABRModel, SABRParams

class InterestRatePricerSABR:
    def __init__(self, curve, beta: float = 0.5):
        self.curve = curve
        self.model = SABRModel(beta=beta)
        self.params_by_expiry: Dict[float, SABRParams] = {}

    def set_params(self, T: float, params: SABRParams):
        self.params_by_expiry[T] = params

    def implied_vol(self, F: float, K: float, T: float) -> float:
        p = self.params_by_expiry.get(T)
        if p is None:
            raise ValueError(f"No SABR params for T={T}")
        return self.model.hagan_implied_vol(F, K, T, p)

    def price_swaption(self, notional: float, T_expiry: float, swap_tenor: float, strike: float, payer: bool = True, freq: int = 1) -> float:
        F = self.curve.forward_swap_rate(T_expiry, T_expiry + swap_tenor, freq=freq)
        vol = self.implied_vol(F, strike, T_expiry)
        pay_times = np.arange(T_expiry + 1 / freq, T_expiry + swap_tenor + 1e-12, 1 / freq)
        dfs = np.array([self.curve.df(t) for t in pay_times])
        annuity = float(np.sum(dfs) * (1.0 / freq))
        df_expiry = self.curve.df(T_expiry)
        price_per_unit = black_price(F, strike, T_expiry, vol, df_expiry, call=payer)
        return float(notional * annuity * price_per_unit / df_expiry)

    def price_cap(self, notional: float, K: float, maturities: List[float], freq: int = 4) -> float:
        price = 0.0
        for i in range(len(maturities) - 1):
            T1, T2 = maturities[i], maturities[i+1]
            tau = T2 - T1
            df1, df2 = self.curve.df(T1), self.curve.df(T2)
            F = (df1/df2 - 1.0) / tau
            p = self.params_by_expiry.get(T1, SABRParams(alpha=0.04, beta=self.model.beta, rho=-0.2, nu=0.4))
            vol = self.model.hagan_implied_vol(F, K, T1, p)
            caplet = notional * tau * black_price(F, K, T1, vol, self.curve.df(T1), call=True)
            price += caplet
        return float(price)

    def price_floor(self, notional: float, K: float, maturities: List[float], freq: int = 4) -> float:
        price = 0.0
        for i in range(len(maturities) - 1):
            T1, T2 = maturities[i], maturities[i+1]
            tau = T2 - T1
            df1, df2 = self.curve.df(T1), self.curve.df(T2)
            F = (df1/df2 - 1.0) / tau
            p = self.params_by_expiry.get(T1, SABRParams(alpha=0.04, beta=self.model.beta, rho=-0.2, nu=0.4))
            vol = self.model.hagan_implied_vol(F, K, T1, p)
            floorlet = notional * tau * black_price(F, K, T1, vol, self.curve.df(T1), call=False)
            price += floorlet
        return float(price)
