# ===========================================
# Evaluación en IRIS con múltiples clasificadores
# Métricas: MAE, MSE, RMSE, R2, Precision, Recall, F1 (macro)
# ===========================================
import numpy as np
import pandas as pd

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

# Métricas
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    mean_absolute_error, mean_squared_error, r2_score
)

# -------------------------
# 1) Datos y split
# -------------------------
iris = load_iris()
X, y = iris.data, iris.target     # y ya viene como 0,1,2, pero usamos LabelEncoder por claridad
le = LabelEncoder().fit(y)
y_num = le.transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
y_train_num, y_test_num = le.transform(y_train), le.transform(y_test)

# -------------------------
# 2) Definición de modelos
# (escalamos cuando conviene)
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

for nombre, modelo in modelos:
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    # Métricas de clasificación (macro = promedio entre clases)
    precision = precision_score(y_test, y_pred, average='macro', zero_division=0)
    recall    = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1        = f1_score(y_test, y_pred, average='macro', zero_division=0)
    acc       = accuracy_score(y_test, y_pred)

    # Métricas "de regresión" sobre etiquetas codificadas (solo demostración)
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

# -------------------------
# 4) Mostrar tabla ordenada por F1
# -------------------------
df = pd.DataFrame(resultados).sort_values(by="F1-Score(macro)", ascending=False)
pd.set_option("display.max_columns", None)
print(df.to_string(index=False))

# (Opcional) ver el mejor modelo y su desempeño rápido
mejor = df.iloc[0]
print("\nMejor por F1-Score(macro):", mejor["Modelo"])
print(mejor)
