# -*- coding: utf-8 -*-
"""
Evaluación de clasificadores en Titanic:
- Visualización "en crudo" (PCA 2D numérico) + barras de clases
- Segmentación train/test y visualización (PCA 2D sobre datos preprocesados)
- Entrenamiento y evaluación de 10 clasificadores
- Métricas: Accuracy, Precision (macro/weighted), Recall (macro/weighted), F1 (macro/weighted)
- Matrices de confusión por clasificador
- Tabla comparativa + gráficas de barras
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    ConfusionMatrixDisplay
)

# Clasificadores solicitados
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# ---------------------------------------------------------------------
# 1) Carga del CSV
# ---------------------------------------------------------------------
CSV_PATH = "Titanic-Dataset.csv"  # <-- ajusta si tu archivo tiene otro nombre/ruta
df = pd.read_csv(CSV_PATH)

# ---------------------------------------------------------------------
# 2) Detección de columna objetivo
#    (por defecto probamos nombres típicos, ej. 'Survived')
# ---------------------------------------------------------------------
def detectar_objetivo(df):
    candidatos = ['survived', 'target', 'label', 'class', 'y']
    cols_lower = {c.lower(): c for c in df.columns}
    for name in candidatos:
        if name in cols_lower:
            return cols_lower[name]
    # Si no se encontró, heurística: si existe una columna binaria con 0/1 y nombre intuitivo
    for c in df.columns:
        serie = df[c].dropna().unique()
        if len(serie) <= 10 and set(serie).issubset({0, 1, "0", "1", "yes", "no", "Yes", "No"}):
            return c
    # Si no, como fallback, intenta 'Survived' con cualquier capitalización
    for c in df.columns:
        if c.lower() == 'survived':
            return c
    # Si nada aplica, pide elegir manualmente
    raise ValueError(
        "No pude detectar la columna objetivo automáticamente. "
        "Renombra tu columna objetivo a 'Survived' (o pasa una de ['target','label','class','y'])."
    )

target_col = detectar_objetivo(df)

print(f"Columna objetivo detectada: {target_col}")

# ---------------------------------------------------------------------
# 3) Separación X/y
# ---------------------------------------------------------------------
y = df[target_col]
X = df.drop(columns=[target_col])

# ---------------------------------------------------------------------
# 4) Visualización "en crudo" (antes de hacerle algo)
#    - PCA 2D con solo columnas numéricas tal cual
#    - Barras de distribución de clases
# ---------------------------------------------------------------------
def plot_crudo_pca_y_clases(X, y, outdir="figs"):
    os.makedirs(outdir, exist_ok=True)
    # Solo numéricas en crudo
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) >= 2:
        X_num = X[num_cols].copy()
        X_num = X_num.replace([np.inf, -np.inf], np.nan).fillna(X_num.median(numeric_only=True))
        # Estandarizar un poco para PCA crudo (opcional)
        X_scaled = (X_num - X_num.mean(numeric_only=True)) / X_num.std(numeric_only=True).replace(0, 1)
        X_scaled = X_scaled.fillna(0)

        pca = PCA(n_components=2, random_state=RANDOM_STATE)
        Z = pca.fit_transform(X_scaled)

        plt.figure(figsize=(7,6))
        classes = pd.Series(y).astype(str)
        for cls in classes.unique():
            idx = (classes == cls)
            plt.scatter(Z[idx,0], Z[idx,1], s=20, alpha=0.7, label=str(cls))
        plt.title("PCA 2D (CRUDO) con columnas numéricas")
        plt.xlabel("PC1"); plt.ylabel("PC2")
        plt.legend(title="Clase")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "crudo_pca_2d.png"), dpi=160)
        plt.close()
    else:
        print("No hay suficientes columnas numéricas para PCA crudo (se necesitan >=2).")

    # Barras de distribución de clases
    plt.figure(figsize=(5,4))
    pd.Series(y).value_counts().sort_index().plot(kind='bar')
    plt.title("Distribución de clases (CRUDO)")
    plt.xlabel("Clase"); plt.ylabel("Conteo")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "crudo_distribucion_clases.png"), dpi=160)
    plt.close()

plot_crudo_pca_y_clases(X, y, outdir="figs")

# ---------------------------------------------------------------------
# 5) Preprocesamiento con ColumnTransformer
#    - Numéricas: imputación (mediana) + estandarización
#    - Categóricas: imputación (más frecuente) + one-hot
# ---------------------------------------------------------------------
from sklearn.impute import SimpleImputer

numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()

# Compatibilidad para sparse_output (>=1.2) o sparse (<=1.1)
try:
    ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
except TypeError:
    ohe = OneHotEncoder(handle_unknown='ignore', sparse=False)

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", ohe)
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ],
    remainder="drop"  # mantenemos sólo columnas procesadas
)

# ---------------------------------------------------------------------
# 6) Segmentación train/test (estratificada)
#    y visualización PCA de datos ya preprocesados (train vs test)
# ---------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

def plot_segmentado_pca(preprocessor, X_train, X_test, outdir="figs"):
    os.makedirs(outdir, exist_ok=True)

    # Ajustamos el preprocesador SOLO con train
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)

    # PCA 2D sobre datos preprocesados (train+test juntos pero coloreados distinto)
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    Z_train = pca.fit_transform(X_train_proc)
    Z_test = pca.transform(X_test_proc)

    plt.figure(figsize=(7,6))
    plt.scatter(Z_train[:,0], Z_train[:,1], s=20, alpha=0.7, label="Train")
    plt.scatter(Z_test[:,0], Z_test[:,1], s=20, alpha=0.7, label="Test", marker='x')
    plt.title("PCA 2D (Datos SEGMENTADOS y PREPROCESADOS)")
    plt.xlabel("PC1"); plt.ylabel("PC2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "segmentado_pca_2d.png"), dpi=160)
    plt.close()

plot_segmentado_pca(preprocessor, X_train, X_test, outdir="figs")

# ---------------------------------------------------------------------
# 7) Definición de clasificadores (exactamente los solicitados)
# ---------------------------------------------------------------------
modelos = {
    "KNeighborsClassifier": KNeighborsClassifier(),
    "SVC": SVC(probability=False, random_state=RANDOM_STATE),
    "LinearSVC": LinearSVC(random_state=RANDOM_STATE),
    "NuSVC": NuSVC(probability=False, random_state=RANDOM_STATE),
    "DecisionTree": DecisionTreeClassifier(random_state=RANDOM_STATE),
    "RandomForest": RandomForestClassifier(random_state=RANDOM_STATE),
    "AdaBoost": AdaBoostClassifier(random_state=RANDOM_STATE),
    "GradientBoosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    "GaussianNB": GaussianNB(),
    "MLPClassifier": MLPClassifier(max_iter=500, random_state=RANDOM_STATE)
}

# ---------------------------------------------------------------------
# 8) Entrenamiento, métricas y matrices de confusión
# ---------------------------------------------------------------------
def evaluar_modelos(modelos, preprocessor, X_train, X_test, y_train, y_test, outdir="figs"):
    os.makedirs(outdir, exist_ok=True)
    registros = []

    for nombre, clf in modelos.items():
        # Pipeline: preprocesamiento + modelo
        pipe = Pipeline(steps=[
            ("prep", preprocessor),
            ("clf", clf)
        ])

        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        # Métricas
        acc = accuracy_score(y_test, y_pred)
        prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
        rec_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)

        prec_weighted = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec_weighted = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        registros.append({
            "modelo": nombre,
            "accuracy": acc,
            "precision_macro": prec_macro,
            "recall_macro": rec_macro,
            "f1_macro": f1_macro,
            "precision_weighted": prec_weighted,
            "recall_weighted": rec_weighted,
            "f1_weighted": f1_weighted
        })

        # Matriz de confusión (normalizada y sin normalizar)
        fig, ax = plt.subplots(1, 2, figsize=(10,4))
        ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax[0], colorbar=False)
        ax[0].set_title(f"{nombre} - Confusión")

        ConfusionMatrixDisplay.from_predictions(y_test, y_pred, normalize='true', ax=ax[1], colorbar=False)
        ax[1].set_title(f"{nombre} - Confusión (normalizada)")

        plt.tight_layout()
        figpath = os.path.join(outdir, f"cm_{nombre}.png")
        plt.savefig(figpath, dpi=160)
        plt.close()

    resultados = pd.DataFrame(registros).sort_values(by="f1_weighted", ascending=False).reset_index(drop=True)
    # Guardar CSV con métricas
    resultados.to_csv(os.path.join(outdir, "metricas_resumen.csv"), index=False)
    return resultados

resultados = evaluar_modelos(modelos, preprocessor, X_train, X_test, y_train, y_test, outdir="figs")

print("\n=== Resumen de métricas (ordenado por F1 weighted) ===")
print(resultados.round(4))

# ---------------------------------------------------------------------
# 9) Gráficas de barras de métricas comparativas
# ---------------------------------------------------------------------
def plot_metric_bars(resultados, outdir="figs"):
    os.makedirs(outdir, exist_ok=True)

    def _barplot(colname, titulo, fname):
        plt.figure(figsize=(10,5))
        idx = np.arange(len(resultados))
        plt.bar(idx, resultados[colname].values)
        plt.xticks(idx, resultados["modelo"].values, rotation=45, ha="right")
        plt.ylabel(colname)
        plt.title(titulo)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, fname), dpi=160)
        plt.close()

    _barplot("accuracy", "Accuracy por modelo", "bar_accuracy.png")
    _barplot("precision_macro", "Precision (macro) por modelo", "bar_precision_macro.png")
    _barplot("recall_macro", "Recall (macro) por modelo", "bar_recall_macro.png")
    _barplot("f1_macro", "F1-score (macro) por modelo", "bar_f1_macro.png")

    _barplot("precision_weighted", "Precision (weighted) por modelo", "bar_precision_weighted.png")
    _barplot("recall_weighted", "Recall (weighted) por modelo", "bar_recall_weighted.png")
    _barplot("f1_weighted", "F1-score (weighted) por modelo", "bar_f1_weighted.png")

plot_metric_bars(resultados, outdir="figs")

# ---------------------------------------------------------------------
# 10) Notas útiles de salida
# ---------------------------------------------------------------------
print("\nArchivos generados en ./figs :")
print("- crudo_pca_2d.png")
print("- crudo_distribucion_clases.png")
print("- segmentado_pca_2d.png")
print("- cm_<Modelo>.png (10 archivos)")
print("- bar_*.png (barras de métricas)")
print("- metricas_resumen.csv (tabla con todas las métricas)")

