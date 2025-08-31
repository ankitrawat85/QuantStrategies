# Flat Methods Export

This folder contains one standalone script per method extracted from your original `main_trendline_stream.py`:

- `method_ols.py` — `fit_ols_line`, `fit_constrained_ols`
- `method_huber.py` — `fit_huber_line` (imports `fit_ols_line` from `method_ols`)
- `method_hough.py` — `hough_lines`
- `method_envelope.py` — `compute_envelope_for_line`, `apply_envelope_if_ols_env`

## Example usage

```python
import numpy as np
from method_ols import fit_ols_line, fit_constrained_ols
from method_huber import fit_huber_line
from method_hough import hough_lines
from method_envelope import compute_envelope_for_line, apply_envelope_if_ols_env

# X, Y are np arrays of indices/prices
m, b = fit_ols_line(X, Y)

# Huber robust line
m_h, b_h = fit_huber_line(X, Y)

# Hough lines
lines = hough_lines(X, Y)  # supply params per your original signature

# Envelopes for OLS variants
upper, lower = compute_envelope_for_line(X, Y, m, b, mode="atr", base=14, k=2.0)
```

Place these files next to your script (or on PYTHONPATH). Keep the filenames as-is so
`method_huber.py` can import `method_ols.py`.
