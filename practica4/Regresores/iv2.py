# ============================================================
# v2 DEBUG — Regressors en Iris (regresión de 'petal length (cm)')
# Muestra paso a paso: carga de datos, X/y, pipelines, split demo,
# particiones KFold, CV de 3 folds (raw) y CV final RepeatedKFold (5x5)
# Métricas: MAE, MSE, RMSE, R2
# ============================================================

import warnings
import numpy as np
import pandas as pd

from sklearn.datasets import load_iris
from sklearn.model_selection import (
    train_test_split, KFold, RepeatedKFold, cross_validate
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.exceptions import ConvergenceWarning

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

# Para que no ensucie la consola si MLP tarda en converger:
warnings.filterwarnings("ignore", category=ConvergenceWarning)

np.set_printoptions(precision=4, suppress=True)
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 10)

def hr(title=""):
    print("\n" + "=" * 80)
    if title:
        print(title)
        print("-" * 80)

# ----------------------------------------------------------------------------------
# 0) IMPORTS
# ----------------------------------------------------------------------------------
hr("0) IMPORTS OK — librerías cargadas")

# ----------------------------------------------------------------------------------
# 1) Cargar Iris y mirar su “forma” (filas x columnas)
# ----------------------------------------------------------------------------------
hr("1) CARGA DEL DATASET IRIS")
iris = load_iris(as_frame=True)
df = iris.frame  # DataFrame con 4 medidas + target (especie)

print("Columnas numéricas:", iris.feature_names)
print("\nPrimeras 5 filas:")
print(df.head())

print("\nForma del DataFrame (filas, columnas):", df.shape)
print("Descripción estadística (resumen rápido):")
print(df.describe())

# ----------------------------------------------------------------------------------
# 2) Separar X (features) e y (target) para regresión
#    y = 'petal length (cm)' ; X = otras 3 columnas
# ----------------------------------------------------------------------------------
hr("2) SELECCIÓN DE FEATURES Y TARGET (REGRESIÓN)")
target_col = 'petal length (cm)'
feature_cols = [c for c in iris.feature_names if c != target_col]

X = df[feature_cols].copy()
y = df[target_col].copy()

print("Target (y):", target_col)
print("Features (X):", feature_cols)
print("Forma de X:", X.shape, "| Forma de y:", y.shape)

print("\nPrimeras 3 filas de X:")
print(X.head(3))
print("\nPrimeras 3 filas de y:")
print(y.head(3))

# Un vistazo rápido a correlaciones (para entender por qué funciona bien):
print("\nMatriz de correlaciones entre columnas numéricas (incluye el target):")
print(df[iris.feature_names].corr().round(3))

# ----------------------------------------------------------------------------------
# 3) Definir modelos como Pipelines y ver sus pasos
#    (KNN y MLP requieren escalado; RF y Linear no estrictamente)
# ----------------------------------------------------------------------------------
hr("3) DEFINICIÓN DE MODELOS/PIPES")
models = {
    "LinearRegression": make_pipeline(LinearRegression()),
    "KNeighborsRegressor": make_pipeline(
        StandardScaler(),
        KNeighborsRegressor(n_neighbors=5, weights='distance')
    ),
    "RandomForestRegressor": make_pipeline(
        RandomForestRegressor(n_estimators=300, random_state=42)
    ),
    "MLPRegressor": make_pipeline(
        StandardScaler(),
        MLPRegressor(
            hidden_layer_sizes=(64, 64),
            activation="relu",
            random_state=42,
            early_stopping=True,
            max_iter=2000,
            learning_rate_init=1e-3
        )
    ),
}

for name, pipe in models.items():
    print(f"\n{name} → pasos del pipeline:")
    print(pipe)

print("\nNota: StandardScaler aparece en KNN/MLP porque usan distancias/gradientes; "
      "RandomForest/Linear no lo requieren estrictamente.")

# ----------------------------------------------------------------------------------
# 4) DEMO rápido con train/test split para ver predicciones crudas de un pipeline
# ----------------------------------------------------------------------------------
hr("4) DEMO TRAIN/TEST SPLIT con KNN (mostrar predicciones vs reales)")
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)
demo = models["KNeighborsRegressor"]

print("Tamaños → train:", X_tr.shape, "| test:", X_te.shape)
print("Fitteando pipeline DEMO (KNN)...")
demo.fit(X_tr, y_tr)
y_pred_demo = demo.predict(X_te)

print("\nPrimeras 10 predicciones (redondeadas) vs reales:")
for i in range(10):
    print(f"  pred={y_pred_demo[i]:.3f} | real={y_te.iloc[i]:.3f}")

mae_demo  = mean_absolute_error(y_te, y_pred_demo)
rmse_demo = mean_squared_error(y_te, y_pred_demo, squared=False)
r2_demo   = r2_score(y_te, y_pred_demo)

print("\nMétricas del split DEMO (solo 1 partición):")
print(f"  MAE  = {mae_demo:.4f}")
print(f"  RMSE = {rmse_demo:.4f}")
print(f"  R2   = {r2_demo:.4f}")

# ----------------------------------------------------------------------------------
# 5) Mostrar cómo KFold divide índices (modo debug)
# ----------------------------------------------------------------------------------
hr("5) EJEMPLO KFOLD: cómo se particiona (n_splits=3)")
kf = KFold(n_splits=3, shuffle=True, random_state=42)
fold_id = 1
for tr_idx, te_idx in kf.split(X):
    print(f"Fold {fold_id} → train: {len(tr_idx)} filas, test: {len(te_idx)} filas")
    print("  Índices test (primeros 12):", te_idx[:12])
    fold_id += 1

# ----------------------------------------------------------------------------------
# 6) CV corta con 3 folds para ver ARRAYS CRUDOS de métricas por fold (Linear)
# ----------------------------------------------------------------------------------
hr("6) CV CORTA (3 folds) — MÉTRICAS CRUDAS por fold para LinearRegression")
scoring = {
    "MAE":  "neg_mean_absolute_error",
    "MSE":  "neg_mean_squared_error",
    "RMSE": "neg_root_mean_squared_error",
    "R2":   "r2",
}

name = "LinearRegression"
pipe = models[name]
scores = cross_validate(pipe, X, y, cv=kf, scoring=scoring, return_train_score=False)

print("Dict de scores (raw):")
for k, v in scores.items():
    print(f"  {k}: {np.array(v)}")

# Convertimos a positivo para leerlo “bonito”
mae  = -scores["test_MAE"]
mse  = -scores["test_MSE"]
rmse = -scores["test_RMSE"]
r2   =  scores["test_R2"]

print("\nConvertidas a escala positiva:")
print("  MAE por fold :", np.round(mae, 4))
print("  MSE por fold :", np.round(mse, 4))
print("  RMSE por fold:", np.round(rmse, 4))
print("  R2 por fold  :", np.round(r2, 4))

print("\nResumen (mean ± std):")
print(f"  MAE  : {mae.mean():.4f} ± {mae.std(ddof=1):.4f}")
print(f"  RMSE : {rmse.mean():.4f} ± {rmse.std(ddof=1):.4f}")
print(f"  R2   : {r2.mean():.4f} ± {r2.std(ddof=1):.4f}")

# ----------------------------------------------------------------------------------
# 7) CV FINAL — RepeatedKFold (5 folds × 5 repeticiones = 25 particiones)
# ----------------------------------------------------------------------------------
hr("7) CV FINAL — RepeatedKFold(5x5) para TODOS los modelos")
cv = RepeatedKFold(n_splits=5, n_repeats=5, random_state=42)

rows = []
for name, pipe in models.items():
    print(f"\nEvaluando {name} con CV 5x5 ...")
    scores = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=-1, return_train_score=False)

    mae  = -scores["test_MAE"]
    mse  = -scores["test_MSE"]
    rmse = -scores["test_RMSE"]
    r2   =  scores["test_R2"]

    # Debug rápido: muestra 5 valores de cada métrica
    print("  (Debug) 5 valores de MAE:",  np.round(mae[:5], 4))
    print("  (Debug) 5 valores de RMSE:", np.round(rmse[:5], 4))
    print("  (Debug) 5 valores de R2:",   np.round(r2[:5], 4))

    rows.append({
        "Modelo": name,
        "MAE (mean)":  mae.mean(),   "MAE (std)":  mae.std(ddof=1),
        "MSE (mean)":  mse.mean(),   "MSE (std)":  mse.std(ddof=1),
        "RMSE (mean)": rmse.mean(),  "RMSE (std)": rmse.std(ddof=1),
        "R2 (mean)":   r2.mean(),    "R2 (std)":   r2.std(ddof=1),
    })

results = pd.DataFrame(rows).sort_values(by="RMSE (mean)").reset_index(drop=True)

print("\n=== RESULTADOS FINALES (ordenados por RMSE medio; menor es mejor) ===")
print(results.to_string(index=False))

# Ganador por RMSE
best_row = results.iloc[0]
print("\nGANADOR por RMSE (mean) ↓")
print(f"  Modelo: {best_row['Modelo']}")
print(f"  RMSE (mean) = {best_row['RMSE (mean)']:.4f}  |  RMSE (std) = {best_row['RMSE (std)']:.4f}")
print(f"  MAE  (mean) = {best_row['MAE (mean)']:.4f}  |  R2   (mean) = {best_row['R2 (mean)']:.4f}")

# (Opcional) Guardar resultados:
out_path = "iris_regression_cv_results.csv"
results.to_csv(out_path, index=False)
print(f"\nResultados guardados en: {out_path}")
