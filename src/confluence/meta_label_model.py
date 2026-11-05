"""
LightGBM Meta-Labeling Classifier
Trains strictly on 5-Year Training set to predict whether a 9-pillar aligned setup hits Target 1 before micro-invalidation.
Filters live/test execution to signals with P(Win) >= 0.95.
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from typing import Optional, Tuple

class MetaLabelModel:
    def __init__(self, min_train_samples: int = 100, min_win_prob: float = 0.95):
        self.min_train_samples = min_train_samples
        self.min_win_prob = min_win_prob
        self.model: Optional[lgb.LGBMClassifier] = None
        self.pipeline: Optional[Pipeline] = None
        self.is_trained = False

    def _build_pipeline(self):
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("lgbm", lgb.LGBMClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                num_leaves=31,
                random_state=42,
                verbose=-1
            ))
        ])

    def train(self, X: pd.DataFrame, y: np.ndarray) -> dict:
        if len(X) < self.min_train_samples:
            raise ValueError(f"Insufficient training samples: {len(X)} < {self.min_train_samples}")
        
        self._build_pipeline()
        self.pipeline.fit(X, y)
        self.is_trained = True

        train_acc = self.pipeline.score(X, y)
        return {
            "train_samples": len(X),
            "train_accuracy": round(train_acc, 4),
            "n_features": X.shape[1]
        }

    def predict_win_probability(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        return self.pipeline.predict_proba(X)[:, 1]

    def should_trade(self, X: pd.DataFrame) -> Tuple[bool, float]:
        proba = self.predict_win_probability(X)
        p = proba[0]
        return (p >= self.min_win_prob), float(p)

    def save(self, path: str):
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model.")
        import joblib
        joblib.dump(self.pipeline, path)

    def load(self, path: str):
        import joblib
        self.pipeline = joblib.load(path)
        self.is_trained = True

class MetaLabelFeatureGenerator:
    FEATURE_COLUMNS = [
        "p1_replenishment_ratio", "p2_poc_distance", "p3_net_gex", "p3_zero_gamma_distance",
        "p4_imbalance_ratio", "p5_wall_age", "p6_sweep_size", "p7_cvd_divergence",
        "p8_vwap_distance", "p9_amt_regime", "e1_vpin", "e2_lpsr", "e3_charm",
        "e3_vanna", "e4_iceberg_ratio", "e5_ev_ratio", "confluence_score"
    ]

    @staticmethod
    def generate_features(snapshots: pd.DataFrame) -> pd.DataFrame:
        features = snapshots[MetaLabelFeatureGenerator.FEATURE_COLUMNS].copy()
        return features

    @staticmethod
    def generate_labels(snapshots: pd.DataFrame, target_1_ticks: float = 5.0) -> np.ndarray:
        if "hit_target_1" in snapshots.columns:
            return snapshots["hit_target_1"].values
        return np.zeros(len(snapshots))
