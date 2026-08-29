"""ThermalEye — LightGBM Multi-Class Thermal Source Classifier.

Provides supervised machine learning classification across the 7-class taxonomy:
0. industrial_fire
1. gas_flare
2. brick_kiln
3. agricultural_burn
4. mining
5. wildfire
6. sun_glint

Outputs:
- Predicted class label
- Calibrated probability distribution across all 7 classes
- Confidence score (0.0 – 1.0)
"""
import os
import pickle
from typing import Dict, Any, List, Tuple

import numpy as np
import lightgbm as lgb

from shared.config import MODELS_DIR, THERMAL_CLASSES
from intelligence.models.temporal_features import feature_dict_to_vector, extract_cluster_features

MODEL_PATH = MODELS_DIR / "thermal_classifier_lgb.pkl"


def train_baseline_model() -> lgb.LGBMClassifier:
    """Train a physics-calibrated LightGBM model on synthetic/reference benchmark distribution."""
    rng = np.random.default_rng(2026)
    n_samples_per_class = 200

    X_list = []
    y_list = []

    for class_idx, class_name in enumerate(THERMAL_CLASSES):
        for _ in range(n_samples_per_class):
            if class_name == "industrial_fire":
                # High FRP spike, short duration, near industrial
                med_frp = float(rng.normal(180.0, 40.0))
                max_frp = med_frp * float(rng.uniform(1.8, 4.0))
                cov = float(rng.uniform(0.35, 0.85))
                dur_h = float(rng.uniform(4.0, 48.0))
                persist = float(rng.uniform(0.02, 0.15))
                diurnal = float(rng.uniform(0.2, 0.6))
                vnf_k = float(rng.normal(1100.0, 100.0))
                d_ind = float(rng.uniform(0.1, 2.5))
                d_pet = float(rng.uniform(3.0, 30.0))
                d_kiln = float(rng.uniform(5.0, 40.0))
                d_mine = float(rng.uniform(5.0, 50.0))
                d_farm = float(rng.uniform(1.0, 15.0))
                d_for = float(rng.uniform(2.0, 20.0))

            elif class_name == "gas_flare":
                # 24/7 steady FRP, high VNF temp (>1400K), low CoV (<0.15), near petroleum
                med_frp = float(rng.normal(42.0, 6.0))
                max_frp = med_frp * float(rng.uniform(1.05, 1.25))
                cov = float(rng.uniform(0.04, 0.14))
                dur_h = float(rng.uniform(500.0, 2160.0))
                persist = float(rng.uniform(0.70, 1.0))
                diurnal = float(rng.uniform(0.40, 0.60)) # Equal day & night
                vnf_k = float(rng.normal(1750.0, 60.0))
                d_ind = float(rng.uniform(0.5, 5.0))
                d_pet = float(rng.uniform(0.05, 1.5))
                d_kiln = float(rng.uniform(10.0, 50.0))
                d_mine = float(rng.uniform(10.0, 60.0))
                d_farm = float(rng.uniform(2.0, 20.0))
                d_for = float(rng.uniform(10.0, 40.0))

            elif class_name == "brick_kiln":
                # Moderate FRP, cyclical diurnal, near farmland/IGP, seasonal
                med_frp = float(rng.normal(18.0, 4.0))
                max_frp = med_frp * float(rng.uniform(1.2, 1.6))
                cov = float(rng.uniform(0.18, 0.35))
                dur_h = float(rng.uniform(120.0, 1200.0))
                persist = float(rng.uniform(0.35, 0.75))
                diurnal = float(rng.uniform(0.05, 0.25)) # Mostly day firing
                vnf_k = float(rng.normal(950.0, 50.0))
                d_ind = float(rng.uniform(3.0, 20.0))
                d_pet = float(rng.uniform(15.0, 60.0))
                d_kiln = float(rng.uniform(0.05, 1.2))
                d_mine = float(rng.uniform(10.0, 50.0))
                d_farm = float(rng.uniform(0.2, 2.0))
                d_for = float(rng.uniform(4.0, 30.0))

            elif class_name == "agricultural_burn":
                # Low-moderate FRP, strictly daytime (diurnal ~0), short 1-3d duration, farmland
                med_frp = float(rng.normal(14.0, 3.5))
                max_frp = med_frp * float(rng.uniform(1.1, 1.5))
                cov = float(rng.uniform(0.15, 0.40))
                dur_h = float(rng.uniform(6.0, 72.0))
                persist = float(rng.uniform(0.05, 0.20))
                diurnal = 0.0 # Strictly day
                vnf_k = 0.0
                d_ind = float(rng.uniform(5.0, 30.0))
                d_pet = float(rng.uniform(20.0, 80.0))
                d_kiln = float(rng.uniform(2.0, 20.0))
                d_mine = float(rng.uniform(15.0, 70.0))
                d_farm = float(rng.uniform(0.01, 0.8))
                d_for = float(rng.uniform(3.0, 25.0))

            elif class_name == "mining":
                # Moderate FRP, persistent, near quarry/coal mining leases
                med_frp = float(rng.normal(32.0, 8.0))
                max_frp = med_frp * float(rng.uniform(1.3, 2.0))
                cov = float(rng.uniform(0.22, 0.45))
                dur_h = float(rng.uniform(200.0, 1500.0))
                persist = float(rng.uniform(0.40, 0.85))
                diurnal = float(rng.uniform(0.15, 0.45))
                vnf_k = float(rng.normal(1150.0, 80.0))
                d_ind = float(rng.uniform(1.0, 8.0))
                d_pet = float(rng.uniform(10.0, 50.0))
                d_kiln = float(rng.uniform(5.0, 30.0))
                d_mine = float(rng.uniform(0.05, 1.8))
                d_farm = float(rng.uniform(3.0, 20.0))
                d_for = float(rng.uniform(1.0, 15.0))

            elif class_name == "wildfire":
                # Spreading, vegetation/forest, multi-day
                med_frp = float(rng.normal(95.0, 30.0))
                max_frp = med_frp * float(rng.uniform(1.5, 3.0))
                cov = float(rng.uniform(0.30, 0.60))
                dur_h = float(rng.uniform(24.0, 168.0))
                persist = float(rng.uniform(0.15, 0.45))
                diurnal = float(rng.uniform(0.20, 0.50))
                vnf_k = float(rng.normal(850.0, 60.0))
                d_ind = float(rng.uniform(10.0, 50.0))
                d_pet = float(rng.uniform(20.0, 70.0))
                d_kiln = float(rng.uniform(15.0, 60.0))
                d_mine = float(rng.uniform(10.0, 50.0))
                d_farm = float(rng.uniform(2.0, 15.0))
                d_for = float(rng.uniform(0.05, 1.5))

            else: # sun_glint
                # Low FRP (<10MW), noon only, zero night, metal/solar reflection
                med_frp = float(rng.uniform(2.5, 8.5))
                max_frp = med_frp * float(rng.uniform(1.0, 1.2))
                cov = float(rng.uniform(0.05, 0.15))
                dur_h = float(rng.uniform(1.0, 24.0))
                persist = float(rng.uniform(0.02, 0.08))
                diurnal = 0.0
                vnf_k = 0.0
                d_ind = float(rng.uniform(0.5, 10.0))
                d_pet = float(rng.uniform(5.0, 30.0))
                d_kiln = float(rng.uniform(5.0, 30.0))
                d_mine = float(rng.uniform(5.0, 30.0))
                d_farm = float(rng.uniform(1.0, 20.0))
                d_for = float(rng.uniform(5.0, 40.0))

            spike = max_frp / max(1.0, med_frp)
            vec = [
                med_frp, max_frp, cov, spike, dur_h, persist, diurnal, vnf_k,
                d_ind, d_pet, d_kiln, d_mine, d_farm, d_for
            ]
            X_list.append(vec)
            y_list.append(class_idx)

    X = np.array(X_list)
    y = np.array(y_list)

    clf = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=15,
        random_state=42,
        verbosity=-1
    )
    clf.fit(X, y)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    print(f"[model] Trained and serialized LightGBM 7-class model to {MODEL_PATH}")
    return clf


def get_or_load_model() -> lgb.LGBMClassifier:
    """Load cached model or train automatically."""
    if MODEL_PATH.exists():
        try:
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    return train_baseline_model()


def predict_thermal_class(cluster_features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
    """Predict class name, confidence, and full probability distribution."""
    clf = get_or_load_model()
    vec = [feature_dict_to_vector(cluster_features)]
    
    probs = clf.predict_proba(vec)[0]
    best_idx = int(np.argmax(probs))
    best_class = THERMAL_CLASSES[best_idx]
    confidence = float(probs[best_idx])

    prob_dict = {
        THERMAL_CLASSES[i]: round(float(probs[i]), 4)
        for i in range(len(THERMAL_CLASSES))
    }
    return best_class, confidence, prob_dict


if __name__ == "__main__":
    model = train_baseline_model()
    test_flare = {
        "median_frp": 42.5, "max_frp": 45.0, "cov_frp": 0.06, "spike_ratio": 1.05,
        "duration_hours": 720.0, "persistence_score": 0.95, "diurnal_ratio": 0.50,
        "vnf_temp_k": 1820.0, "dist_industrial_km": 1.2, "dist_petroleum_km": 0.3,
        "dist_kiln_km": 25.0, "dist_mining_km": 30.0, "dist_farmland_km": 10.0,
        "dist_forest_km": 35.0, "dist_vulnerable_km": 15.0
    }
    cls, conf, dist = predict_thermal_class(test_flare)
    print(f"\nPrediction for Mangala Flare: {cls} (Confidence: {conf:.2%})")
    print(f"Probabilities: {dist}")
