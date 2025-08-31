"""
method_ols_shift_min.py
Thin wrapper that fits OLS, then shifts the intercept so the line hugs price from
below (support, side="S") or above (resistance, side="R") by aligning to the
min/max residual ("shift-min" style).

Exports:
    - fit_ols_shift_min_line(x, y, side, tol_abs=0.0)
      returns (m, b) for the shifted line
"""
from __future__ import annotations
import numpy as np
from .method_ols import fit_ols_line

def fit_ols_shift_min_line(x, y, side: str = "S", tol_abs: float = 0.0):
    """
    Parameters
    ----------
    x : array-like
        Integer or float index positions (e.g., np.arange(n)).
    y : array-like
        Prices to fit against (e.g., highs for R, lows for S, or close/hl2).
    side : {"S","R"}
        "S" for support (line should be <= prices), "R" for resistance (>= prices).
    tol_abs : float, optional
        Extra absolute tolerance to push the line further away from price if desired.

    Returns
    -------
    (m, b) : tuple(float, float)
        The slope and intercept of the shifted line.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size != y.size:
        raise ValueError("x and y must be same length")

    # Base OLS
    m, b = fit_ols_line(x, y)

    # Residuals of the *unshifted* line
    r = y - (m * x + b)

    if str(side).upper().startswith("R"):
        # For resistance: line >= y  ⇒ delta ≥ max(r). Choose tightest: delta = max(r).
        delta = float(np.max(r)) if r.size else 0.0
        b2 = b + delta + float(tol_abs)
    else:
        # For support (default): line <= y ⇒ delta ≤ min(r). Choose tightest: delta = min(r).
        delta = float(np.min(r)) if r.size else 0.0
        b2 = b + delta - float(tol_abs)

    return float(m), float(b2)
