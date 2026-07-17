from __future__ import annotations
import threading
import numpy as np

class _Arm:
    __slots__ = ('A', 'b', 'A_inv', 'theta')

    def __init__(self, dim: int) -> None:
        self.A = np.identity(dim)
        self.b = np.zeros(dim)
        self.A_inv = np.identity(dim)
        self.theta = np.zeros(dim)

    def refresh(self) -> None:
        self.A_inv = np.linalg.inv(self.A)
        self.theta = self.A_inv @ self.b

class LinUCB:

    def __init__(self, dim: int, alpha: float=0.6) -> None:
        self.dim = dim
        self.alpha = alpha
        self._arms: dict[str, _Arm] = {}
        self._lock = threading.Lock()

    def _arm(self, arm: str) -> _Arm:
        a = self._arms.get(arm)
        if a is None:
            a = self._arms[arm] = _Arm(self.dim)
        return a

    def score(self, arm: str, x: np.ndarray) -> float:
        a = self._arm(arm)
        mean = float(a.theta @ x)
        explore = self.alpha * float(np.sqrt(x @ a.A_inv @ x))
        return mean + explore

    def update(self, arm: str, x: np.ndarray, reward: float) -> None:
        with self._lock:
            a = self._arm(arm)
            a.A += np.outer(x, x)
            a.b += reward * x
            a.refresh()
