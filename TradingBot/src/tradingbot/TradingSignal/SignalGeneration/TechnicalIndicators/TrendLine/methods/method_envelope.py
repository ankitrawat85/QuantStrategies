"""Envelope helpers for OLS variants (env/shift_min) extracted from your script."""
import numpy as np

def compute_envelope_for_line(line, df, mode="atr", env_base=14, env_k=2.0):
    """
    Compute upper/lower channel for a given trendline.
    Expects: line.slope, line.intercept, line.start_idx, line.end_idx
    Returns dict with 'upper','lower','mid' as lists of (i, y).
    """
    import numpy as np
    n = len(df)
    start = int(getattr(line, "start_idx", 0))
    end   = int(getattr(line, "end_idx", n - 1))
    if end < start:
        start, end = end, start
    xs = np.arange(start, min(end, n - 1) + 1, dtype=int)
    mids = line.slope * xs + line.intercept

    if mode == "atr" and "atr" in df.columns:
        atr_roll = df["atr"].rolling(int(max(1, env_base)), min_periods=1).mean()
        half = env_k * atr_roll.iloc[xs].to_numpy()
    elif mode == "pct":
        half = (float(env_k) * 0.01) * mids
    else:  # "abs" or fallback
        half = float(env_k)
        half = np.full_like(mids, half, dtype=float)

    upper = mids + half
    lower = mids - half
    return {
        "mid":   list(zip(xs.tolist(), mids.tolist())),
        "upper": list(zip(xs.tolist(), upper.tolist())),
        "lower": list(zip(xs.tolist(), lower.tolist())),
    }

def apply_envelope_if_ols_env(method, line, df, args, fig=None, name_prefix="env"):
    """
    Call this right after you create the Line.
    If method == "ols_env", compute envelope & optionally add to `fig` (Plotly or Matplotlib).
    Returns the envelope dict (or None).
    """
    if method != "ols_env" or line is None:
        return None

    # Ensure ATR exists if using ATR mode
    try:
        if getattr(args, "env_mode", "atr") == "atr" and "atr" not in df.columns:
            try:
                atr_len = getattr(args, "atr_len", 14) if hasattr(args, "atr_len") else 14
                if "atr_wilder" in globals():
                    df["atr"] = atr_wilder(df, atr_len)
            except Exception:
                pass
    except Exception:
        pass

    try:
        env = compute_envelope_for_line(
            line, df,
            mode=getattr(args, "env_mode", "atr"),
            env_base=getattr(args, "env_base", 14),
            env_k=getattr(args, "env_k", 2.0)
        )
    except Exception as e:
        print("Envelope computation failed:", e)
        return None

    # Build x-axis
    try:
        xs = [df.index[i] for (i, _) in env["upper"]]
    except Exception:
        xs = [i for (i, _) in env["upper"]]

    # Plotly overlay
    try:
        import plotly.graph_objects as go
        if fig is not None and hasattr(fig, "add_trace"):
            fig.add_trace(go.Scatter(x=xs, y=[y for (_, y) in env["upper"]],
                                     mode="lines", name=f"{name_prefix}↑", opacity=0.5))
            fig.add_trace(go.Scatter(x=xs, y=[y for (_, y) in env["lower"]],
                                     mode="lines", name=f"{name_prefix}↓", opacity=0.5))
    except Exception:
        # Matplotlib fallback
        try:
            import matplotlib.pyplot as plt
            if fig is None:
                plt.plot(xs, [y for (_, y) in env["upper"]], label=f"{name_prefix}↑")
                plt.plot(xs, [y for (_, y) in env["lower"]], label=f"{name_prefix}↓")
        except Exception:
            pass

    return env