
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    accuracy_score,
    classification_report,
)

BASE_DIR = Path(__file__).resolve().parent
DATASET = BASE_DIR / "dataset" / "electricity_bill_dataset.csv"
FOLDER_MODEL = BASE_DIR / "models_ml"

FOLDER_MODEL.mkdir(exist_ok=True)

# Membaca dataset
df = pd.read_csv(DATASET)

# Fitur dan target
fitur = [
    "Fan",
    "Refrigerator",
    "AirConditioner",
    "Television",
    "Monitor",
    "MotorPump",
    "Month",
    "City",
    "Company",
    "MonthlyHours",
    "TariffRate",
]

target = "ElectricityBill"

X = df[fitur]
y = df[target]

# Membuat kategori berdasarkan sepertiga distribusi biaya
batas = y.quantile([1/3, 2/3]).values

kategori = pd.cut(
    y,
    bins=[-np.inf, batas[0], batas[1], np.inf],
    labels=["HEMAT", "NORMAL", "TINGGI"],
    include_lowest=True,
)

# Memisahkan kolom numerik dan kategorikal
kolom_kategori = ["City", "Company"]
kolom_numerik = [kolom for kolom in fitur if kolom not in kolom_kategori]

preprocessor = ColumnTransformer(
    transformers=[
        ("numerik", "passthrough", kolom_numerik),
        ("kategori", OneHotEncoder(handle_unknown="ignore"), kolom_kategori),
    ]
)

# Model regresi
model_regresi = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        n_jobs=-1
    )),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model_regresi.fit(X_train, y_train)
prediksi_regresi = model_regresi.predict(X_test)

print("\n=== HASIL MODEL REGRESI ===")
print("MAE:", round(mean_absolute_error(y_test, prediksi_regresi), 2))
print("R2 Score:", round(r2_score(y_test, prediksi_regresi), 4))

# Model klasifikasi
X_train_k, X_test_k, y_train_k, y_test_k = train_test_split(
    X,
    kategori,
    test_size=0.2,
    random_state=42,
    stratify=kategori,
)

model_klasifikasi = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        n_jobs=-1
    )),
])

model_klasifikasi.fit(X_train_k, y_train_k)
prediksi_k = model_klasifikasi.predict(X_test_k)

print("\n=== HASIL MODEL KLASIFIKASI ===")
print("Accuracy:", round(accuracy_score(y_test_k, prediksi_k), 4))
print(classification_report(y_test_k, prediksi_k))

# Menyimpan model baru
joblib.dump(model_regresi, FOLDER_MODEL / "model_regresi.pkl")
joblib.dump(model_klasifikasi, FOLDER_MODEL / "model_klasifikasi.pkl")
joblib.dump(fitur, FOLDER_MODEL / "fitur_model.pkl")
joblib.dump(batas.tolist(), FOLDER_MODEL / "batas_kategori.pkl")

print("\nMODEL BARU BERHASIL DISIMPAN!")
