from __future__ import annotations
import pickle
from pathlib import Path
import numpy as np
from app import config
try:
    from econml.metalearners import XLearner
    _HAS_ECONML = True
except Exception:
    _HAS_ECONML = False
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

class UpliftModel:

    def __init__(self, version: str) -> None:
        self.name = 'uplift'
        self.version = version
        self.algo = 'econml-xlearner' if _HAS_ECONML else 'sklearn-tlearner'
        self._treated = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        self._control = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        self._x = None

    def fit(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> 'UpliftModel':
        if _HAS_ECONML:
            self._x = XLearner(models=LogisticRegression(max_iter=1000), propensity_model=LogisticRegression(max_iter=1000))
            self._x.fit(Y, T, X=X)
        else:
            self._treated.fit(X[T == 1], Y[T == 1])
            self._control.fit(X[T == 0], Y[T == 0])
        return self

    def uplift(self, vector: list[float]) -> float:
        x = np.asarray(vector, dtype=float).reshape(1, -1)
        if _HAS_ECONML and self._x is not None:
            return float(np.clip(self._x.effect(x)[0], -1.0, 1.0))
        p_t = self._treated.predict_proba(x)[0][1]
        p_c = self._control.predict_proba(x)[0][1]
        return float(np.clip(p_t - p_c, -1.0, 1.0))

    def _path(self) -> Path:
        return config.ARTIFACTS_DIR / f'{self.name}.pkl'

    def save(self) -> None:
        with open(self._path(), 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls) -> 'UpliftModel':
        with open(config.ARTIFACTS_DIR / 'uplift.pkl', 'rb') as f:
            return pickle.load(f)
