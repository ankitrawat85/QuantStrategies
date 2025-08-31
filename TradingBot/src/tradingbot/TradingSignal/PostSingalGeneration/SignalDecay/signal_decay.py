from dataclasses import dataclass
from typing import Tuple
import numpy as np

@dataclass
class DecayParams:
    decay_lambda: float | None = None
    decay_hold: int = 0
    decay_threshold: float = 0.0

    @classmethod
    def from_obj(cls, obj) -> "DecayParams":
        if obj is None:
            return cls()
        get = (lambda k, d=None: getattr(obj, k, d) if hasattr(obj, k) else obj.get(k, d) if isinstance(obj, dict) else d)
        return cls(
            decay_lambda=get('decay_lambda', None),
            decay_hold=int(get('decay_hold', 0) or 0),
            decay_threshold=float(get('decay_threshold', 0.0) or 0.0),
        )

def compute_decay_weights(ds, decay_lambda, decay_hold):
    ds = np.asarray(ds, dtype=int)
    if decay_lambda is None or float(decay_lambda) <= 0:
        return np.ones_like(ds, dtype=float)
    hold = int(decay_hold) if decay_hold is not None else 0
    dec = np.ones_like(ds, dtype=float)
    after = ds - hold
    mask = after > 0
    dec[mask] = np.exp(-float(decay_lambda) * after[mask])
    return dec

def apply_decay(conf, ds, decay_lambda, decay_hold):
    conf = np.asarray(conf, dtype=float)
    dec = compute_decay_weights(ds, decay_lambda, decay_hold)
    return conf * dec

def threshold_mask(effective_values, threshold):
    thr = float(threshold) if threshold is not None else 0.0
    return np.asarray(effective_values, dtype=float) >= thr

def apply_decay_and_threshold(conf, ds, params: DecayParams) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    dec = compute_decay_weights(ds, params.decay_lambda, params.decay_hold)
    eff = np.asarray(conf, dtype=float) * dec
    keep = threshold_mask(eff, params.decay_threshold)
    return dec, eff, keep
