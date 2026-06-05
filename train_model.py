import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import pickle

METHOD_MAP = {"GET": 0, "POST": 1, "PUT": 2, "DELETE": 3}
PATH_PATTERNS = ["/products/", "/stock", "/users", "/admin", "/debug", "/internal"]
RAZON_KEYWORDS = ["scraping", "stock sin consultar", "nocturna", "repetitiva", "stock repetitivas", "recon_attack"]

def encode_method(method):
    return METHOD_MAP.get(str(method).upper(), -1)

def encode_path(path):
    for i, pattern in enumerate(PATH_PATTERNS):
        if pattern in str(path):
            return i
    return len(PATH_PATTERNS)

def encode_flags(flags):
    flags = str(flags).lower() if flags else ""
    return {
        "flag_night":      int("night_hours" in flags),
        "flag_pressure":   int("system_pressure" in flags),
        "flag_recidivist": int("recidivist" in flags),
    }

def encode_razones(razones):
    razones = str(razones).lower() if razones else ""
    return {f"razon_{i}": int(kw in razones) for i, kw in enumerate(RAZON_KEYWORDS)}

df = pd.read_csv("dataset_full.csv")
df["recon_correlated"] = df["recon_correlated"].map({"t": 1, "f": 0, True: 1, False: 0}).fillna(0)
df["method_enc"] = df["action_method"].fillna("GET").apply(encode_method)
df["path_enc"]   = df["action_path"].fillna("/").apply(encode_path)

flags_df  = df["adaptive_flags"].apply(lambda x: pd.Series(encode_flags(x)))
razon_df  = df["razones"].apply(lambda x: pd.Series(encode_razones(x)))
df = pd.concat([df, flags_df, razon_df], axis=1)

FEATURES = [
    "score", "recon_correlated", "history_len", "long_history_len",
    "method_enc", "path_enc",
    "flag_night", "flag_pressure", "flag_recidivist",
    "razon_0", "razon_1", "razon_2", "razon_3", "razon_4", "razon_5",
]

X = df[FEATURES]
y = df["decision"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))

le = LabelEncoder()
le.fit(y)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print(f"Clases: {list(le.classes_)}")
print("Guardado: model.pkl + label_encoder.pkl")
