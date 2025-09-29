# ===========================================
# IRIS + múltiples clasificadores
# Métricas: Accuracy, Precision/Recall/F1 (macro),
#           MAE, MSE, RMSE, R2
# Extra: classification report y matriz de confusión
# ===========================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline

# Clasificadores de la diapositiva
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

# Métricas y visualizaciones
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    mean_absolute_error, mean_squared_error, r2_score,
    classification_report, confusion_matrix, ConfusionMatrixDisplay
)

# -------- Config --------
PLOT_ALL_MODELS = False  # pon True si quieres ver la matriz de confusión de TODOS los modelos

# -------------------------
# 1) Datos y split
# -------------------------
iris = load_iris()
X, y = iris.data, iris.target
class_names = iris.target_names

le = LabelEncoder().fit(y)
y_num = le.transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
y_train_num, y_test_num = le.transform(y_train), le.transform(y_test)

# -------------------------
# 2) Definición de modelos
# -------------------------
def pipe(clf, use_scaler=False):
    return Pipeline([('scaler', StandardScaler()), ('clf', clf)]) if use_scaler else clf

modelos = [
    ("KNeighborsClassifier", pipe(KNeighborsClassifier(), use_scaler=True)),
    ("SVC",               pipe(SVC(probability=True, random_state=42), use_scaler=True)),
    ("LinearSVC",         pipe(LinearSVC(random_state=42), use_scaler=True)),
    ("NuSVC",             pipe(NuSVC(probability=True, random_state=42), use_scaler=True)),
    ("DecisionTreeClassifier", DecisionTreeClassifier(random_state=42)),
    ("RandomForestClassifier", RandomForestClassifier(n_estimators=300, random_state=42)),
    ("AdaBoostClassifier",     AdaBoostClassifier(random_state=42)),
    ("GradientBoostingClassifier", GradientBoostingClassifier(random_state=42)),
    ("GaussianNB", GaussianNB()),
    ("MLPClassifier", pipe(MLPClassifier(hidden_layer_sizes=(100,),
                                         max_iter=1000, random_state=42), use_scaler=True)),
]

# -------------------------
# 3) Entrenamiento y métricas
# -------------------------
resultados = []
predicciones_por_modelo = {}  # guardamos para luego graficar

for nombre, modelo in modelos:
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    # Clasificación
    precision = precision_score(y_test, y_pred, average='macro', zero_division=0)
    recall    = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1        = f1_score(y_test, y_pred, average='macro', zero_division=0)
    acc       = accuracy_score(y_test, y_pred)

    # "Regresión" sobre etiquetas (propósito didáctico)
    y_pred_num = le.transform(y_pred)
    mae  = mean_absolute_error(y_test_num, y_pred_num)
    mse  = mean_squared_error(y_test_num, y_pred_num)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_test_num, y_pred_num)

    resultados.append({
        "Modelo": nombre,
        "Accuracy": acc,
        "Precision(macro)": precision,
        "Recall(macro)": recall,
        "F1-Score(macro)": f1,
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2,
    })

    predicciones_por_modelo[nombre] = (modelo, y_pred)

# -------------------------
# 4) Tabla ordenada + mejor modelo
# -------------------------
df = pd.DataFrame(resultados).sort_values(by="F1-Score(macro)", ascending=False)
pd.set_option("display.max_columns", None)
print("\n=== Resultados ===")
print(df.to_string(index=False))

mejor_nombre = df.iloc[0]["Modelo"]
mejor_modelo, mejor_y_pred = predicciones_por_modelo[mejor_nombre]
print(f"\nMejor por F1-Score(macro): {mejor_nombre}")

# -------------------------
# 5) Classification report del mejor modelo
# -------------------------
print("\n=== Classification report (mejor modelo) ===")
print(classification_report(y_test, mejor_y_pred, target_names=class_names, zero_division=0))

# -------------------------
# 6) Matriz de confusión
# -------------------------
def plot_confmat(y_true, y_pred, etiquetas, titulo="Matriz de confusión"):
    cm = confusion_matrix(y_true, y_pred, labels=range(len(etiquetas)))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=etiquetas)
    fig, ax = plt.subplots(figsize=(5, 4))
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    plt.title(titulo)
    plt.tight_layout()
    plt.show()

# Mejor modelo
plot_confmat(y_test, mejor_y_pred, class_names, titulo=f"Confusion Matrix - {mejor_nombre}")

# (Opcional) Matriz para todos los modelos
if PLOT_ALL_MODELS:
    for nombre, (_, y_pred) in predicciones_por_modelo.items():
        plot_confmat(y_test, y_pred, class_names, titulo=f"Confusion Matrix - {nombre}")
