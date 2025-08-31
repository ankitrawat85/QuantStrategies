# config_utils.py
SKIP = {"methods", "methods_to_run"}

def method_params(cfg: dict, method: str) -> dict:
    """Flat dict for `method`: prefer methods.<method> → fall back to top-level."""
    cfg = cfg or {}
    top  = {k: v for k, v in cfg.items() if k not in SKIP}
    meth = (cfg.get("methods", {}) or {}).get(method, {}) or {}
    # Treat blanks as missing so they don't override real values
    meth = {k: v for k, v in meth.items() if not (isinstance(v, str) and v == "")}
    return {**top, **meth}

def cfg_get(cfg: dict, method: str, key: str, default=None, cast=None):
    """Single-key getter with method-first then top-level fallback."""
    m = (cfg or {}).get("methods", {}).get(method, {}) or {}
    val = m.get(key, (cfg or {}).get(key, default))
    if isinstance(val, str) and val == "":  # blank = missing
        val = default
    if cast and val is not None:
        val = cast(val)
    return val
