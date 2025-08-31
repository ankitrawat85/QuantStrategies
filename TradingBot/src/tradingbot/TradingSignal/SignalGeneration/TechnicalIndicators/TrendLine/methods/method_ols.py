"""OLS-based trendline methods extracted from your script."""
import numpy as np

def fit_ols_line(x, y):
    X = np.vstack([x, np.ones_like(x)]).T
    m, b = np.linalg.lstsq(X, y, rcond=None)[0]
    return float(m), float(b)

def fit_constrained_ols(x, y_fit_ref, c_bound, side, eps=1e-9):
    """
    Solve  min_{m,b} sum_i (y_fit_ref[i] - (m*x[i] + b))^2
    s.t.   resistance (side=='R'):  m*x[i] + b >= c_bound[i]   (typically highs + tol_abs)
           support   (else)       :  m*x[i] + b <= c_bound[i]   (typically lows  - tol_abs)

    Strategy:
      (A) Try unconstrained OLS → if feasible, return it.
      (B) Minimal intercept shift holding OLS slope → feasible.
      (C) All pairwise active-constraint candidates (two points on the bound) → keep feasible ones.
      Pick the feasible candidate with minimum SSE vs y_fit_ref.
    """
    x = np.asarray(x, float)
    y = np.asarray(y_fit_ref, float)
    c = np.asarray(c_bound, float)
    n = len(x)
    assert x.shape == y.shape == c.shape and n >= 2

    # (A) Unconstrained OLS
    X = np.vstack([x, np.ones_like(x)]).T
    m0, b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    line0 = m0 * x + b0
    feas0 = np.all(line0 >= c - eps) if side == "R" else np.all(line0 <= c + eps)
    if feas0:
        return float(m0), float(b0)

    # candidate list
    candidates = []

    # (B) Minimal intercept shift with OLS slope
    if side == "R":
        b_shift = np.max(c - m0 * x)
    else:
        b_shift = np.min(c - m0 * x)
    candidates.append((float(m0), float(b_shift)))

    # (C) Pairwise active constraints
    for i in range(n - 1):
        xi, ci = x[i], c[i]
        for j in range(i + 1, n):
            xj, cj = x[j], c[j]
            if xi == xj:
                continue
            m = (ci - cj) / (xi - xj)
            b = ci - m * xi
            y_line = m * x + b
            feasible = np.all(y_line >= c - eps) if side == "R" else np.all(y_line <= c + eps)
            if feasible:
                candidates.append((float(m), float(b)))

    # fallback (shouldn't happen): use minimal shift
    if not candidates:
        return (float(m0), float(b_shift))

    # choose min-SSE candidate
    best, best_sse = None, np.inf
    for (m, b) in candidates:
        sse = np.sum((y - (m * x + b))**2)
        if sse < best_sse:
            best_sse = sse
            best = (m, b)
    return best