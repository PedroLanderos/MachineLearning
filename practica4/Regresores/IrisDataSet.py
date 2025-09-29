# ============================================================
# Regressors en Iris (regresión de 'petal length (cm)')
# Métricas: MAE, MSE, RMSE, R2 con validación cruzada
# ============================================================

import numpy as np
import pandas as pd

from sklearn.datasets import load_iris
from sklearn.model_selection import RepeatedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

# -----------------------------
# 1) Cargar Iris como DataFrame
# -----------------------------
iris = load_iris(as_frame=True)
df = iris.frame  # contiene X + target (la especie), pero no usaremos 'target' aquí
target_col = 'petal length (cm)'                     # y
feature_cols = [c for c in iris.feature_names if c != target_col]  # X = 3 columnas restantes
X = df[feature_cols]
y = df[target_col]

# ---------------------------------------------
# 2) Definir modelos (con pipelines cuando toca)
#    - KNN y MLP necesitan escalado de características
#    - RandomForest no lo necesita, Linear tampoco
# ---------------------------------------------
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
            early_stopping=True,    # para evitar sobreajuste con tan pocos datos
            max_iter=2000,
            learning_rate_init=1e-3
        )
    )
}

# ----------------------------------------
# 3) Validación cruzada y métricas a medir
#    - RepeatedKFold = 5 folds repetidos 5 veces (25 particiones)
#    - Scikit-learn devuelve las pérdidas "neg_*": luego invertimos el signo
# ----------------------------------------
cv = RepeatedKFold(n_splits=5, n_repeats=5, random_state=42)
scoring = {
    "MAE":  "neg_mean_absolute_error",
    "MSE":  "neg_mean_squared_error",
    "RMSE": "neg_root_mean_squared_error",
    "R2":   "r2",
}

# -------------------------------------------
# 4) Ejecutar CV y tabular medias y desviaciones
# -------------------------------------------
rows = []
for name, pipe in models.items():
    scores = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=-1, return_train_score=False)
    
    # Convertir las métricas negativas a positivas
    mae  = -scores["test_MAE"]
    mse  = -scores["test_MSE"]
    rmse = -scores["test_RMSE"]
    r2   =  scores["test_R2"]
    
    rows.append({
        "Modelo": name,
        "MAE (mean)":  mae.mean(),   "MAE (std)":  mae.std(ddof=1),
        "MSE (mean)":  mse.mean(),   "MSE (std)":  mse.std(ddof=1),
        "RMSE (mean)": rmse.mean(),  "RMSE (std)": rmse.std(ddof=1),
        "R2 (mean)":   r2.mean(),    "R2 (std)":   r2.std(ddof=1),
    })

results = pd.DataFrame(rows).sort_values(by="RMSE (mean)")
print(results.to_string(index=False))
