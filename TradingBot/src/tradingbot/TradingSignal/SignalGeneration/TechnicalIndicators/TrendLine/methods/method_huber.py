"""Huber-regression trendline method extracted from your script.

Depends on fit_ols_line from method_ols when initializing parameters.
"""
import numpy as np
from .method_ols import fit_ols_line

def fit_huber_line(x, y, delta=1.0, iters=30, eps=1e-8):
    m, b = fit_ols_line(x, y)
    X = np.vstack([x, np.ones_like(x)]).T
    for _ in range(iters):
        r = y - (m*x + b)
        w = np.where(np.abs(r) <= delta, 1.0, delta / (np.abs(r) + eps))
        WX = X * w[:,None]; Wy = y * w
        m_new, b_new = np.linalg.lstsq(WX, Wy, rcond=None)[0]
        if abs(m_new-m) < 1e-9 and abs(b_new-b) < 1e-6:
            m, b = float(m_new), float(b_new); break
        m, b = float(m_new), float(b_new)
    return m, b