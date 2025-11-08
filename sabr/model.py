from dataclasses import dataclass
import numpy as np

@dataclass
class SABRParams:
    alpha: float
    beta: float
    rho: float
    nu: float

class SABRModel:
    def __init__(self, beta: float = 0.5):
        self.beta = beta

    @staticmethod
    def _z_chi(F, K, alpha, beta, rho, nu):
        if F == K:
            return 0.0, 1.0
        one_minus_beta = 1.0 - beta
        FK = (F * K) ** (0.5 * one_minus_beta)
        logFK = np.log(F / K)
        z = (nu / alpha) * FK * logFK
        a = np.sqrt(1 - 2 * rho * z + z**2) + z - rho
        b = 1 - rho
        chi = np.log(a / b)
        return z, chi

    @staticmethod
    def hagan_implied_vol(F: float, K: float, T: float, p: 'SABRParams') -> float:
        alpha, beta, rho, nu = p.alpha, p.beta, p.rho, p.nu
        if F <= 0 or K <= 0 or alpha <= 0:
            return 0.0
        one_minus_beta = 1.0 - beta
        FK = (F * K) ** (0.5 * one_minus_beta)
        logFK = 0.0 if F == K else np.log(F / K)
        z, chi = SABRModel._z_chi(F, K, alpha, beta, rho, nu)
        denom = FK * (1 + (one_minus_beta**2 / 24.0) * logFK**2 + (one_minus_beta**4 / 1920.0) * logFK**4)
        A = 1 + ((one_minus_beta**2 / 24.0) * (alpha**2) / (FK**2) + (rho * beta * nu * alpha) / (4.0 * FK) + ((2 - 3 * rho**2) / 24.0) * (nu**2)) * T
        if abs(F - K) < 1e-12:
            vol = (alpha / denom) * A
        else:
            vol = (alpha / denom) * (z / chi) * A
        return max(float(vol), 0.0)
