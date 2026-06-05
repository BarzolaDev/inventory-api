"""
api/services/ml_predictor.py

Carga model.pkl + label_encoder.pkl y expone predict_behavior()
para que agent_defender.py lo use como señal adicional.

Uso desde agent_defender.py:
    from api.services.ml_predictor import predict_behavior

    label, confidence = predict_behavior(
        score=request_score,
        history_len=short_history,
        long_history_len=long_history,
        recon_correlated=True,
        action_method="GET",
        action_path="/products/123",
        adaptive_flags="night_hours,recidivist",
        razones="recon_attack,scraping",
    )
"""

import pickle
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ─── Constantes (deben coincidir con train_model.py) ──────────────────────────

METHOD_MAP = {"GET": 0, "POST": 1, "PUT": 2, "DELETE": 3}

PATH_PATTERNS = [
    "/products/",
    "/stock",
    "/users",
    "/admin",
    "/debug",
    "/internal",
]

RAZON_KEYWORDS = [
    "scraping",
    "stock sin consultar",
    "nocturna",
    "repetitiva",
    "stock repetitivas",
    "recon_attack",
]

# ─── Carga del modelo (singleton — se carga una sola vez al importar) ─────────

_MODEL = None
_LABEL_ENCODER = None
_MODEL_READY = False


def _load_models():
    global _MODEL, _LABEL_ENCODER, _MODEL_READY

    # Busca los .pkl en el directorio raíz del proyecto
    base = Path(__file__).resolve().parent.parent.parent
    model_path   = base / "model.pkl"
    encoder_path = base / "label_encoder.pkl"

    if not model_path.exists():
        logger.warning(f"[ml_predictor] model.pkl no encontrado en {model_path}. Predictor desactivado.")
        return
    if not encoder_path.exists():
        logger.warning(f"[ml_predictor] label_encoder.pkl no encontrado en {encoder_path}. Predictor desactivado.")
        return

    with open(model_path, "rb") as f:
        _MODEL = pickle.load(f)
    with open(encoder_path, "rb") as f:
        _LABEL_ENCODER = pickle.load(f)

    _MODEL_READY = True
    logger.info(f"[ml_predictor] Modelo cargado. Clases: {list(_LABEL_ENCODER.classes_)}")


_load_models()

# ─── Feature engineering (espejo exacto de train_model.py) ───────────────────

def _encode_method(method: str) -> int:
    return METHOD_MAP.get(str(method).upper(), -1)


def _encode_path(path: str) -> int:
    path = str(path)
    for i, pattern in enumerate(PATH_PATTERNS):
        if pattern in path:
            return i
    return len(PATH_PATTERNS)


def _encode_adaptive_flags(flags: str) -> dict:
    flags = str(flags) if flags else ""
    return {
        "flag_night":      int("night_hours" in flags),
        "flag_pressure":   int("system_pressure" in flags),
        "flag_recidivist": int("recidivist" in flags),
    }


def _encode_razones(razones: str) -> dict:
    razones = str(razones).lower() if razones else ""
    return {
        f"razon_{i}": int(kw in razones)
        for i, kw in enumerate(RAZON_KEYWORDS)
    }


def _build_feature_vector(
    score: float,
    history_len: int,
    long_history_len: int,
    recon_correlated: bool,
    action_method: str,
    action_path: str,
    adaptive_flags: str,
    razones: str,
) -> pd.DataFrame:
    row = {
        "score":            float(score),
        "recon_correlated": int(recon_correlated),
        "history_len":      int(history_len),
        "long_history_len": int(long_history_len),
        "method_enc":       _encode_method(action_method),
        "path_enc":         _encode_path(action_path),
        **_encode_adaptive_flags(adaptive_flags),
        **_encode_razones(razones),
    }
    return pd.DataFrame([row])


# ─── Interfaz pública ─────────────────────────────────────────────────────────

def is_ready() -> bool:
    """Retorna True si el modelo está cargado y listo para predecir."""
    return _MODEL_READY


def predict_behavior(
    score: float,
    history_len: int,
    long_history_len: int,
    recon_correlated: bool,
    action_method: str,
    action_path: str,
    adaptive_flags: str = "",
    razones: str = "",
) -> Optional[tuple[str, float]]:
    """
    Predice la clase de comportamiento de un request.

    Retorna:
        (label, confidence) — ej: ("BLOQUEADO", 0.91)
        None si el modelo no está disponible.

    El caller (agent_defender.py) decide qué hacer con la predicción.
    Este servicio solo predice, no bloquea.
    """
    if not _MODEL_READY:
        return None

    try:
        X = _build_feature_vector(
            score=score,
            history_len=history_len,
            long_history_len=long_history_len,
            recon_correlated=recon_correlated,
            action_method=action_method,
            action_path=action_path,
            adaptive_flags=adaptive_flags,
            razones=razones,
        )

        # Predicción + probabilidades
        label      = _MODEL.predict(X)[0]
        proba      = _MODEL.predict_proba(X)[0]
        confidence = float(np.max(proba))

        logger.debug(f"[ml_predictor] → {label} (confianza: {confidence:.2f})")
        return label, confidence

    except Exception as e:
        logger.error(f"[ml_predictor] Error al predecir: {e}")
        return None