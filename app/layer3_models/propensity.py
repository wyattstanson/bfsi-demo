"""Layer 3 — Models: binary propensity / churn scorer.

Uses XGBoost when it is importable (the named production library); otherwise
falls back to a scikit-learn logistic-regression pipeline.  Either way the
serving contract is identical: `predict_proba(vector) -> float`, so /decide never
knows which trained.

# PROD: swap local artifacts for SageMaker / Databricks Model Serving endpoints.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

from app import config

try:
    from xgboost import XGBClassifier  # type: ignore

    _HAS_XGB = True
except Exception:  # pragma: no cover - depends on wheel availability
    _HAS_XGB = False

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def _new_estimator():
    if _HAS_XGB:
        return XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.15,
            subsample=0.9,
            eval_metric="logloss",
            n_jobs=1,
        )
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))


class BinaryModel:
    """A trained binary classifier with a stable serving contract."""

    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version
        self.algo = "xgboost" if _HAS_XGB else "sklearn-logreg"
        self._est = _new_estimator()
        self._fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BinaryModel":
        self._est.fit(X, y)
        self._fitted = True
        return self

    def predict_proba(self, vector: list[float]) -> float:
        x = np.asarray(vector, dtype=float).reshape(1, -1)
        p = self._est.predict_proba(x)[0][1]
        return float(p)

    # ---- persistence -----------------------------------------------------
    def _path(self) -> Path:
        return config.ARTIFACTS_DIR / f"{self.name}.pkl"

    def save(self) -> None:
        with open(self._path(), "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, name: str) -> "BinaryModel":
        with open(config.ARTIFACTS_DIR / f"{name}.pkl", "rb") as f:
            return pickle.load(f)
