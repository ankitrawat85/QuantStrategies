"""Signal confidence helpers extracted from your existing code.

Drop this file anywhere on your PYTHONPATH and import:
    from signal_confidence import break_confidence

The function signatures are preserved exactly from your current implementation.
"""
import numpy as np

def _sigmoid(x): return 1.0 / (1.0 + np.exp(-x))

def break_confidence(idx, side, m, b, tol_abs, close, atr,
                 persist_n=3, retest_window=6,
                 w_pen=0.5, w_pers=0.3, w_retest=0.2):
    i = int(idx)
    line_i = m*i + b
    pen = (close[i] - line_i) if side=="R" else (line_i - close[i])
    pen_norm = pen / max(1e-8, atr[i])
    pen_score = _sigmoid(pen_norm)
    if pen <= tol_abs: pen_score *= 0.2
    j = min(len(close)-1, i + persist_n)
    idxs = np.arange(i+1, j+1)
    if len(idxs)==0: 
        pers_score = 0.0
    else:
        line_seg = m*idxs + b
        if side=="R":
            pers_hits = np.sum(close[idxs] > line_seg + tol_abs)
        else:
            pers_hits = np.sum(close[idxs] < line_seg - tol_abs)
        pers_score = pers_hits / max(1, len(idxs))
    k = min(len(close)-1, i + retest_window)
    idxs2 = np.arange(i+1, k+1)
    if len(idxs2)==0:
        retest_score = 0.0
    else:
        line_seg2 = m*idxs2 + b
        if side=="R":
            crossed_back = np.any(close[idxs2] < line_seg2 - tol_abs)
        else:
            crossed_back = np.any(close[idxs2] > line_seg2 + tol_abs)
        near = np.any(np.abs(close[idxs2] - line_seg2) <= tol_abs)
        retest_score = 0.0 if crossed_back else (1.0 if near else 0.5)
    conf = float(w_pen*pen_score + w_pers*pers_score + w_retest*retest_score)
    return float(pen_score), float(pers_score), float(retest_score), conf
