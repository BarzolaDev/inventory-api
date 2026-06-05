"""
Entrenamiento del modelo ML para detección de comportamiento.
Usa datos de agent_decisions para clasificar: NORMAL / SOSPECHOSO / BLOQUEADO

Uso:
    python3 train_model.py --db postgresql://user:password@localhost:5432/dbname

Genera:
    model.pkl         — modelo entrenado
    label_encoder.pkl — encoder de clases
    report.txt        — métricas de evaluación
"""

import argparse
import pickle
import json
from collections import Counter

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

# ─── Features a usar ──────────────────────────────────────────────────────────

RAZON_KEYWORDS = [
    "scraping",
    "stock sin consultar",
    "nocturna",
    "repetitiva",
    "stock repetitivas",
    "recon_attack",
]

METHOD_MAP = {"GET": 0, "POST": 1, "PUT": 2, "DELETE": 3}

PATH_PATTERNS = [
    "/products/",
    "/stock",
    "/users",
    "/admin",
    "/debug",
    "/internal",
]

# ─── Feature engineering ──────────────────────────────────────────────────────

def encode_method(method: str) -> int:
    return METHOD_MAP.get(str(method).upper(), -1)

def encode_path(path: str) -> int:
    path = str(path)
    for i, pattern in enumerate(PATH_PATTERNS):
        if pattern in path:
            return i
    return len(PATH_PATTERNS)  # "other"

def encode_adaptive_flags(flags: str) -> dict:
    flags = str(flags) if flags else ""
    return {
        "flag_night":    int("night_hours" in flags),
        "flag_pressure": int("system_pressure" in flags),
        "flag_recidivist": int("recidivist" in flags),
    }

def encode_razones(razones: str) -> dict:
    razones = str(razones).lower() if razones else ""
    return {
        f"razon_{i}": int(kw in razones)
        for i, kw in enumerate(RAZON_KEYWORDS)
    }

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame()

    # Numéricas directas
    features["score"]            = df["score"].fillna(0).astype(float)
    features["history_len"]      = df["history_len"].fillna(0).astype(int)
    features["long_history_len"] = df["long_history_len"].fillna(0).astype(int)
    features["recon_correlated"] = df["recon_correlated"].astype(int)

    # Método HTTP
    features["method_enc"] = df["action_method"].apply(encode_method)

    # Path
    features["path_enc"] = df["action_path"].apply(encode_path)

    # Flags adaptativas
    flags_df = df["adaptive_flags"].apply(encode_adaptive_flags).apply(pd.Series)
    features = pd.concat([features, flags_df], axis=1)

    # Razones (one-hot por keyword)
    razones_df = df["razones"].apply(encode_razones).apply(pd.Series)
    features = pd.concat([features, razones_df], axis=1)

    return features

# ─── Main ─────────────────────────────────────────────────────────────────────

def main(db_url: str, output_dir: str):
    print("[*] Conectando a la DB...")
    engine = create_engine(db_url)
    df = pd.read_sql("SELECT * FROM agent_decisions", engine)
    print(f"    Total registros: {len(df)}")
    print(f"    Distribución: {dict(Counter(df['decision']))}")

    # Features y labels
    print("\n[*] Construyendo features...")
    X = build_features(df)
    y = df["decision"]

    print(f"    Features: {list(X.columns)}")

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    print(f"    Clases: {list(le.classes_)}")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    print(f"\n[*] Train: {len(X_train)}  Test: {len(X_test)}")
    print(f"    Distribución train: {dict(Counter(le.inverse_transform(y_train)))}")

    # SMOTE — balanceo de clases minoritarias
    print("\n[*] Aplicando SMOTE para balancear clases...")
    counts = Counter(y_train)
    min_count = min(counts.values())
    if min_count < 6:
        k = min_count - 1
        print(f"    k_neighbors ajustado a {k} (clase mínima tiene {min_count} muestras)")
        smote = SMOTE(random_state=42, k_neighbors=k)
    else:
        smote = SMOTE(random_state=42)

    X_res, y_res = smote.fit_resample(X_train, y_train)
    print(f"    Distribución post-SMOTE: {dict(Counter(le.inverse_transform(y_res)))}")

    # Entrenar Random Forest
    print("\n[*] Entrenando Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_res, y_res)

    # Cross-validation
    cv_scores = cross_val_score(model, X_res, y_res, cv=5, scoring="f1_weighted")
    print(f"    CV F1 (5-fold): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # Evaluación en test
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=le.classes_)
    cm = confusion_matrix(y_test, y_pred)

    print("\n[*] Reporte de clasificación:")
    print(report)
    print("    Matriz de confusión:")
    print(f"    Clases: {list(le.classes_)}")
    print(cm)

    # Feature importance
    importances = sorted(
        zip(X.columns, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    print("\n[*] Top features:")
    for feat, imp in importances[:8]:
        print(f"    {feat:<25} {imp:.4f}")

    # Guardar modelo
    model_path = f"{output_dir}/model.pkl"
    encoder_path = f"{output_dir}/label_encoder.pkl"
    report_path = f"{output_dir}/report.txt"

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(encoder_path, "wb") as f:
        pickle.dump(le, f)
    with open(report_path, "w") as f:
        f.write(report)
        f.write(f"\nCV F1: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}\n")
        f.write(f"\nFeature importances:\n")
        for feat, imp in importances:
            f.write(f"  {feat:<25} {imp:.4f}\n")

    print(f"\n[✓] Modelo guardado en {model_path}")
    print(f"[✓] Encoder guardado en {encoder_path}")
    print(f"[✓] Reporte guardado en {report_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="postgresql://user:password@localhost:5432/dbname")
    p.add_argument("--output", default=".")
    a = p.parse_args()
    main(a.db, a.output)
