"""Hough transform based line detection extracted from your script."""
import numpy as np

def hough_lines(x, y, piv_idxs, slope_bins=101, intercept_bins=201, top_k=1,
                tol_abs=1.0, min_touches=3):
    if len(piv_idxs) < min_touches: 
        return []
    xs = x[piv_idxs].astype(float); ys = y[piv_idxs].astype(float)
    xr = float(x[-1]-x[0]) if len(x)>1 else 1.0
    yr = float(np.nanmax(y) - np.nanmin(y))
    max_slope = 2.0 * (yr / max(1.0, xr))
    m_grid = np.linspace(-max_slope, max_slope, slope_bins)
    b_min = float(np.nanmin(y) - max_slope * x[-1])
    b_max = float(np.nanmax(y) - (-max_slope) * x[-1])
    b_grid = np.linspace(b_min, b_max, intercept_bins)
    acc = np.zeros((slope_bins, intercept_bins), dtype=np.int32)
    b_vals = ys[:,None] - m_grid[None,:] * xs[:,None]
    bj = np.floor((b_vals - b_min) / (b_max - b_min) * (intercept_bins-1)).astype(int)
    bj = np.clip(bj, 0, intercept_bins-1)
    for i in range(len(xs)):
        acc[np.arange(slope_bins), bj[i]] += 1
    peaks=[]; A=acc.copy()
    for _ in range(top_k*6):
        si, jj = np.unravel_index(np.argmax(A), A.shape)
        votes = int(A[si, jj])
        if votes <= 1: break
        peaks.append((si, jj, votes))
        A[max(0,si-3):min(A.shape[0],si+4), max(0,jj-6):min(A.shape[1],jj+7)] = 0
    lines = []
    for (si, jj, votes) in peaks:
        m = float(m_grid[si]); b = float(b_grid[jj])
        touches = int(np.sum(np.abs(ys - (m*xs + b)) <= tol_abs))
        if touches >= min_touches:
            lines.append(dict(m=m, b=b, touches=touches, votes=votes))
    return sorted(lines, key=lambda d:(-d["votes"], -d["touches"]))[:top_k]