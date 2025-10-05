# -*- coding: utf-8 -*-
"""
Evaluación de múltiples regresores en varios datasets con métricas y gráficas.

Requisitos:
    pip install pandas numpy scikit-learn matplotlib

CSV esperados en el mismo directorio:
    - CarPrice_Assignment.csv
    - concrete_data.csv
    - diabetes_prediction_dataset.csv
    - HousingData.csv
    - Iris.csv
    - WineQT.csv
"""

import os
import warnings
warnings.filterwarnings("ignore")

# --- Evitar errores de Tkinter al guardar figuras ---
import matplotlib
matplotlib.use("Agg")  # backend no interactivo
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor

# ----------------------------
# CONFIGURACIÓN DE DATASETS
# ----------------------------
DATASETS = {
    "Iris.csv": {
        "target": "PetalLengthCm",
        "drop": ["Id"],  # 'Species' se usa como categórica; 'Id' se elimina
    },
    "HousingData.csv": {  # nombre corregido
        "target": "MEDV",
        "drop": [],
    },
    "diabetes_prediction_dataset.csv": {
        "target": "blood_glucose_level",
        "drop": ["diabetes"],  # evitar fuga de label
    },
    "WineQT.csv": {
        "target": "quality",
        "drop": ["Id"],  # ignorado si no existe
    },
    "CarPrice_Assignment.csv": {
        "target": "price",
        "drop": ["car_ID"],
    },
    "concrete_data.csv": {
        "target": "concrete_compressive_strength",
        "drop": [],
    },
}

# ----------------------------
# MODELOS A EVALUAR
# ----------------------------
RANDOM_STATE = 42
MODELOS = {
    "LinearRegression": LinearRegression(),
    "RandomForestRegressor": RandomForestRegressor(
        n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1
    ),
    "KNeighborsRegressor": KNeighborsRegressor(n_neighbors=5),
    "MLPRegressor": MLPRegressor(
        hidden_layer_sizes=(64, 32),
        random_state=RANDOM_STATE,
        max_iter=1000,
        early_stopping=True
    ),
}

# ----------------------------
# HELPERS
# ----------------------------
def make_ohe():
    """
    Crea un OneHotEncoder compatible tanto con scikit-learn >=1.2 (sparse_output)
    como con versiones anteriores (sparse).
    """
    try:
        # versiones nuevas (>=1.2)
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        # versiones viejas (<1.2)
        return OneHotEncoder(handle_unknown="ignore", sparse=False)

def detectar_tipos_columnas(df_X: pd.DataFrame):
    num_cols = df_X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
    cat_cols = [c for c in df_X.columns if c not in num_cols]
    return num_cols, cat_cols

def construir_preprocesador(df_X: pd.DataFrame) -> ColumnTransformer:
    num_cols, cat_cols = detectar_tipos_columnas(df_X)

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", make_ohe()),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return preprocessor

def evaluar_modelos_en_dataset(csv_path: str, target_col: str, drop_cols=None, test_size=0.2, random_state=RANDOM_STATE):
    if drop_cols is None:
        drop_cols = []

    df = pd.read_csv(csv_path)
    if target_col not in df.columns:
        raise ValueError(f"En '{csv_path}' no se encontró la columna objetivo '{target_col}'. "
                         f"Columnas disponibles: {list(df.columns)}")

    drop_existing = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=drop_existing, errors="ignore")

    y = df[target_col]
    X = df.drop(columns=[target_col])

    preprocessor = construir_preprocesador(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    filas = []
    preds_por_modelo = {}

    for nombre, modelo in MODELOS.items():
        pipe = Pipeline(steps=[
            ("preprocess", preprocessor),
            ("model", modelo),
        ])

        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = float(np.sqrt(mse))
        r2 = r2_score(y_test, y_pred)

        filas.append({
            "Modelo": nombre,
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse,
            "R2": r2,
        })
        preds_por_modelo[nombre] = (y_test.to_numpy(), y_pred)

    resultados = pd.DataFrame(filas).sort_values(by="R2", ascending=False).reset_index(drop=True)
    return resultados, preds_por_modelo

def plot_barras_metricas(resultados: pd.DataFrame, nombre_dataset: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    modelos = resultados["Modelo"].tolist()

    plt.figure(figsize=(8, 4.5))
    plt.bar(modelos, resultados["MAE"])
    plt.title(f"{nombre_dataset} - MAE por modelo")
    plt.ylabel("MAE (menor es mejor)")
    plt.xticks(rotation=20); plt.tight_layout()
    mae_path = os.path.join(outdir, f"{nombre_dataset}_MAE.png")
    plt.savefig(mae_path, dpi=150); plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.bar(modelos, resultados["RMSE"])
    plt.title(f"{nombre_dataset} - RMSE por modelo")
    plt.ylabel("RMSE (menor es mejor)")
    plt.xticks(rotation=20); plt.tight_layout()
    rmse_path = os.path.join(outdir, f"{nombre_dataset}_RMSE.png")
    plt.savefig(rmse_path, dpi=150); plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.bar(modelos, resultados["R2"])
    plt.title(f"{nombre_dataset} - R² por modelo")
    plt.ylabel("R² (mayor es mejor)")
    plt.xticks(rotation=20); plt.tight_layout()
    r2_path = os.path.join(outdir, f"{nombre_dataset}_R2.png")
    plt.savefig(r2_path, dpi=150); plt.close()

    return {"MAE": mae_path, "RMSE": rmse_path, "R2": r2_path}

def plot_scatter_mejor_modelo(resultados: pd.DataFrame, preds_por_modelo: dict, nombre_dataset: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    mejor = resultados.iloc[0]["Modelo"]
    y_true, y_pred = preds_por_modelo[mejor]

    min_val = float(np.nanmin([y_true.min(), y_pred.min()]))
    max_val = float(np.nanmax([y_true.max(), y_pred.max()]))

    plt.figure(figsize=(5.5, 5.5))
    plt.scatter(y_true, y_pred, alpha=0.7)
    plt.plot([min_val, max_val], [min_val, max_val])  # diagonal
    plt.xlabel("Valor real"); plt.ylabel("Predicción")
    plt.title(f"{nombre_dataset} - Mejor modelo: {mejor}\nR²={resultados.iloc[0]['R2']:.3f}")
    plt.tight_layout()
    out_path = os.path.join(outdir, f"{nombre_dataset}_BestModel_Scatter.png")
    plt.savefig(out_path, dpi=150); plt.close()
    return out_path

# ----------------------------
# MAIN
# ----------------------------
def main():
    outputs_dir = "outputs"
    os.makedirs(outputs_dir, exist_ok=True)

    resumen_global = []
    rutas_graficas = {}

    for csv_name, cfg in DATASETS.items():
        csv_path = os.path.join(os.getcwd(), csv_name)
        if not os.path.isfile(csv_path):
            print(f"[ADVERTENCIA] No encontré '{csv_name}' en el directorio actual. Me lo salto.")
            continue

        target = cfg["target"]
        drop_cols = cfg.get("drop", [])

        print(f"\n=== Dataset: {csv_name} | target='{target}' ===")
        try:
            resultados, preds_por_modelo = evaluar_modelos_en_dataset(
                csv_path=csv_path,
                target_col=target,
                drop_cols=drop_cols
            )
        except Exception as e:
            print(f"[ERROR] Problema evaluando '{csv_name}': {e}")
            continue

        base = os.path.splitext(os.path.basename(csv_name))[0]
        out_csv = os.path.join(outputs_dir, f"{base}_metricas.csv")
        resultados.to_csv(out_csv, index=False, encoding="utf-8")
        print(f"Métricas guardadas en: {out_csv}")
        print(resultados)

        ds_outdir = os.path.join(outputs_dir, base)
        paths_metricas = plot_barras_metricas(resultados, base, ds_outdir)
        path_scatter = plot_scatter_mejor_modelo(resultados, preds_por_modelo, base, ds_outdir)
        rutas_graficas[base] = {**paths_metricas, "BestScatter": path_scatter}

        mejor_fila = resultados.iloc[0].to_dict()
        mejor_fila["Dataset"] = base
        resumen_global.append(mejor_fila)

    if resumen_global:
        df_resumen = pd.DataFrame(resumen_global)[
            ["Dataset", "Modelo", "MAE", "MSE", "RMSE", "R2"]
        ].sort_values(by="R2", ascending=False)
        out_resumen = os.path.join(outputs_dir, "resumen_mejores_modelos.csv")
        df_resumen.to_csv(out_resumen, index=False, encoding="utf-8")
        print("\n=== RESUMEN: Mejores modelos por dataset (ordenado por R²) ===")
        print(df_resumen)
        print(f"\nResumen guardado en: {out_resumen}")

        plt.figure(figsize=(9, 4.8))
        plt.bar(df_resumen["Dataset"], df_resumen["R2"])
        plt.title("Mejor R² por dataset")
        plt.ylabel("R²")
        plt.xticks(rotation=20)
        plt.tight_layout()
        r2_global_path = os.path.join(outputs_dir, "Mejor_R2_por_dataset.png")
        plt.savefig(r2_global_path, dpi=150)
        plt.close()
        print(f"Gráfica global guardada en: {r2_global_path}")

        print("\nRutas de gráficas generadas por dataset:")
        for ds, paths in rutas_graficas.items():
            print(f"- {ds}:")
            for k, v in paths.items():
                print(f"   {k}: {v}")
    else:
        print("\nNo se generó resumen porque no se encontró ningún CSV.")

if __name__ == "__main__":
    main()
