"""Layer 4 — Decisioning: a LinUCB contextual bandit.

Ranks eligible actions by expected value while still exploring, using the
disjoint LinUCB algorithm (Li et al., 2010).  Each arm keeps A = X'X + I and
b = X'y; the score is  θ·x + α·sqrt(xᵀA⁻¹x)  (exploit + explore).

Learning online is what lets the demo *improve* which action wins per context
rather than serving a static rank.

# PROD: swap for a managed bandit / RL service; persist arm state to the store.
"""
from __future__ import annotations

import threading

import numpy as np


class LinUCB:
    def __init__(self, dim: int, alpha: float = 0.6) -> None:
        self.dim = dim
        self.alpha = alpha
        self._A: dict[str, np.ndarray] = {}
        self._b: dict[str, np.ndarray] = {}
        self._lock = threading.Lock()

    def _arm(self, arm: str):
        if arm not in self._A:
            self._A[arm] = np.identity(self.dim)
            self._b[arm] = np.zeros(self.dim)
        return self._A[arm], self._b[arm]

    def score(self, arm: str, x: np.ndarray) -> float:
        """Upper-confidence-bound score for one arm in context x."""
        with self._lock:
            A, b = self._arm(arm)
            A_inv = np.linalg.inv(A)
            theta = A_inv @ b
        mean = float(theta @ x)
        explore = self.alpha * float(np.sqrt(x @ A_inv @ x))
        return mean + explore

    def update(self, arm: str, x: np.ndarray, reward: float) -> None:
        """Feed back a realized reward to tighten the arm's estimate."""
        with self._lock:
            A, b = self._arm(arm)
            A += np.outer(x, x)
            b += reward * x
