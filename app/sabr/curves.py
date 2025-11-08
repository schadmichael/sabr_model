import numpy as np

class FlatCurve:
    def __init__(self, rate: float):
        self.rate = float(rate)
    def df(self, t: float) -> float:
        return float(np.exp(-self.rate * t))
    def forward_swap_rate(self, T_start: float, T_end: float, freq: int = 1) -> float:
        payment_times = np.arange(T_start + 1/freq, T_end + 1e-12, 1/freq)
        dfs = np.array([self.df(t) for t in payment_times])
        annuity = np.sum(dfs) * (1.0 / freq)
        return 0.0 if annuity <= 0 else (self.df(T_start) - self.df(T_end)) / annuity

class ZeroCurve:
    """Piecewise-linear zero-rate curve; df(t)=exp(-z(t)*t) with z(t) linearly interpolated."""
    def __init__(self, maturities, zero_rates):
        self.t = np.asarray(maturities, dtype=float)
        self.z = np.asarray(zero_rates, dtype=float)
        order = np.argsort(self.t)
        self.t, self.z = self.t[order], self.z[order]
    def zero(self, t: float) -> float:
        if t <= self.t[0]: return float(self.z[0])
        if t >= self.t[-1]: return float(self.z[-1])
        return float(np.interp(t, self.t, self.z))
    def df(self, t: float) -> float:
        if t <= 0: return 1.0
        zt = self.zero(t)
        return float(np.exp(-zt * t))
    def forward_swap_rate(self, T_start: float, T_end: float, freq: int = 1) -> float:
        payment_times = np.arange(T_start + 1/freq, T_end + 1e-12, 1/freq)
        dfs = np.array([self.df(t) for t in payment_times])
        annuity = np.sum(dfs) * (1.0 / freq)
        return 0.0 if annuity <= 0 else (self.df(T_start) - self.df(T_end)) / annuity
