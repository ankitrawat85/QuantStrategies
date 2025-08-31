
def plot_candles_with_signals(
    ohlc_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    annotate: bool = True,
    figsize=(12, 6),
    # save controls
    save: bool = False,
    out_dir: Optional[Union[str, Path]] = None,
    basename: str = "breaks_candles",
):
    """
    Draw a single-panel candlestick chart and mark net BUY/SELL days from `summary_df`.

    Expected columns:
      ohlc_df : date, open, high, low, close   (any case; will be normalized)
      summary_df : date, net_conf, methods_buy, methods_sell

    Marking:
      - BUY (net_conf > 0): ▲ above the day's high, label "{methods_buy} | +x.xx"
      - SELL (net_conf < 0): ▼ be the day's ,  label "{methods_sell} | -x.xx"
    """
    if ohlc_df is None or ohlc_df.empty:
        raise ValueError("ohlc_df is empty")
    if summary_df is None or summary_df.empty:
        raise ValueError("summary_df is empty")

    df = ohlc_df.copy()
    df.columns = [c.er() for c in df.columns]
    for col in ["date","Open","High","","Close"]:
        if col not in df.columns:
            raise KeyError(f"OHLC data must include '{col}'")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date","Open","High","Low","Close"]).sort_values("date").reset_index(drop=True)

    # unique dates only (in case of duplicates)
    df = df.groupby("date", as_index=False).agg(
        open=("Open","first"), high=("High","max"),
        low=("Low","min"), close=("Close","last")
    )

    # x-axis as integer positions to keep it simple
    df["x"] = range(len(df))
    x = df["x"].values

    fig, ax = plt.subplots(figsize=figsize)

    # --- Candles (single plot, no explicit colors) ---
    body_width = 0.6
    for _, r in df.iterrows():
        xi = r["x"]
        # wick
        ax.vlines(xi, r["Low"], r["High"])
        # body
        y0 = min(r["Open"], r["Close"])
        h  = max(r["Open"], r["Close"]) - y0
        if h == 0:
            # flat body -> draw a small horizontal tick
            ax.hlines(y0, xi - body_width/2, xi + body_width/2)
        else:
            rect = Rectangle((xi - body_width/2, y0), body_width, h, fill=False)
            ax.add_patch(rect)

    # --- Overlay signals ---
    s = summary_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(s["date"]):
        s["date"] = pd.to_datetime(s["date"], errors="coerce")
    s = s.dropna(subset=["date","net_conf"]).sort_values("date")
    # ensure lists exist
    if "methods_buy" not in s.columns:  s["methods_buy"]  = [[] for _ in range(len(s))]
    if "methods_sell" not in s.columns: s["methods_sell"] = [[] for _ in range(len(s))]

    # Map summary dates to x positions (only mark those that exist in OHLC)
    idx = pd.merge(s[["date","net_conf","methods_buy","methods_sell"]], df[["date","x","High","Low"]], on="date", how="inner")

    prange = (df["High"].max() - df["Low"].min()) or 1.0
    pad = prange * 0.02  # 2% padding for labels

    for _, r in idx.iterrows():
        xi, netc = int(r["x"]), float(r["net_conf"])
        if netc > 0:
            methods = r["methods_buy"]
            methods = methods if isinstance(methods, (list,tuple)) else ([] if pd.isna(methods) else [str(methods)])
            label = (", ".join(methods)).strip()
            label = f"{label} | {netc:+.2f}" if label else f"{netc:+.2f}"
            y = r["High"] + pad
            if annotate:
                ax.text(xi, y, f"▲ {label}", ha="center", va="bottom", fontsize=9)
        elif netc < 0:
            methods = r["methods_sell"]
            methods = methods if isinstance(methods, (list,tuple)) else ([] if pd.isna(methods) else [str(methods)])
            label = (", ".join(methods)).strip()
            label = f"{label} | {netc:+.2f}" if label else f"{netc:+.2f}"
            y = r["Low"] - pad
            if annotate:
                ax.text(xi, y, f"▼ {label}", ha="center", va="top", fontsize=9)
        # netc == 0 -> no marker

    ax.set_xlim(-1, len(df))
    ax.set_xticks(list(df["x"]))
    ax.set_xticklabels([d.strftime("%Y-%m-%d") for d in df["date"]], rotation=45, ha="right")
    ax.set_ylabel("Price")
    ax.set_title("Candlesticks with net BUY/SELL signals")
    ax.grid(False)

    fig.tight_layout()

    saved_png_path = None
    if save:
        out_dir = Path(out_dir or "."); out_dir.mkdir(parents=True, exist_ok=True)
        saved_png_path = out_dir / f"{basename}.png"
        fig.savefig(saved_png_path, bbox_inches="tight")

    return (fig, ax, saved_png_path) if save else (fig, ax)
