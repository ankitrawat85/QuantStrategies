"""
method_ols_envelop.py
Alias/wrapper to the envelope helpers so a dedicated module exists for the
method name "ols_envelop". This keeps imports consistent with other methods.

Re-exports:
    - compute_envelope_for_line
    - apply_envelope_if_ols_env
"""
from __future__ import annotations
from .method_envelope import compute_envelope_for_line, apply_envelope_if_ols_env  # re-export

