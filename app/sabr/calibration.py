import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
from scipy.optimize import least_squares
from .model import SABRModel, SABRParams
from .black import black_price

@dataclass
class CalibResult:
    params: SABRParams
    loss: float

class SABRCalibrator:
    def __init__(self, beta: float = 0.5):
        self.model = SABRModel(beta=beta)

    def calibrate_to_vols(self, F: float, T: float, strikes: np.ndarray, market_vols: np.ndarray,
                          initial=(0.05, -0.2, 0.5),
                          bounds=((1e-6, -0.999, 1e-6), (5.0, 0.999, 5.0)),
                          beta: Optional[float] = None) -> CalibResult:
        b = self.model.beta if beta is None else beta
        def residuals(x):
            alpha, rho, nu = x
            p = SABRParams(alpha=alpha, beta=b, rho=rho, nu=nu)
            model_vols = np.array([self.model.hagan_implied_vol(F, k, T, p) for k in strikes])
            return model_vols - market_vols
        res = least_squares(residuals, x0=np.array(initial), bounds=bounds, method="trf")
        p = SABRParams(alpha=float(res.x[0]), beta=float(b), rho=float(res.x[1]), nu=float(res.x[2]))
        return CalibResult(params=p, loss=float(np.sum(res.fun**2)))

    def calibrate_to_prices(self, F: float, T: float, strikes: np.ndarray, market_prices: np.ndarray,
                            df: float = 1.0,
                            call: bool = True,
                            initial=(0.05, -0.2, 0.5),
                            bounds=((1e-6, -0.999, 1e-6), (5.0, 0.999, 5.0)),
                            beta: Optional[float] = None) -> CalibResult:
        b = self.model.beta if beta is None else beta
        def residuals(x):
            alpha, rho, nu = x
            p = SABRParams(alpha=alpha, beta=b, rho=rho, nu=nu)
            model_prices = np.array([
                black_price(F, k, T, self.model.hagan_implied_vol(F, k, T, p), df=df, call=call) for k in strikes
            ])
            return model_prices - market_prices
        res = least_squares(residuals, x0=np.array(initial), bounds=bounds, method="trf")
        p = SABRParams(alpha=float(res.x[0]), beta=float(b), rho=float(res.x[1]), nu=float(res.x[2]))
        return CalibResult(params=p, loss=float(np.sum(res.fun**2)))
