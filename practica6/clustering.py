# dbscan_iris_mall_moons_blobs.py
# Aplica DBSCAN a Iris, Mall Customers, Moons y Blobs; imprime métricas en español y guarda gráficas en ./figs/

import os
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris, make_moons, make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

plt.rcParams["figure.dpi"] = 140
os.makedirs("figs", exist_ok=True)

# --------------------------
# Utilidades de métricas/plot
# --------------------------
def compute_metrics(X, labels):
    """
    Calcula Silueta, Calinski-Harabasz y Davies-Bouldin excluyendo el ruido (-1).
    Devuelve dict con None cuando no aplican (p.ej., <2 clusters válidos).
    """
    mask = labels != -1
    labels_nonoise = labels[mask]
    X_nonoise = X[mask]

    unique_clusters = np.unique(labels_nonoise)
    result = {
        "n_clusters": int(len(unique_clusters)),
        "n_noise": int(np.sum(labels == -1)),
        "silhouette": None,
        "calinski_harabasz": None,
        "davies_bouldin": None,
    }

    if X_nonoise.shape[0] > 0 and len(unique_clusters) >= 2:
        result["silhouette"] = float(silhouette_score(X_nonoise, labels_nonoise))
        result["calinski_harabasz"] = float(calinski_harabasz_score(X_nonoise, labels_nonoise))
        result["davies_bouldin"] = float(davies_bouldin_score(X_nonoise, labels_nonoise))

    return result

def print_metrics_es(m):
    """
    Imprime las métrricas con el formato exacto solicitado (4 decimales).
    """
    if m["silhouette"] is None:
        print("Coeficiente de Silueta: N/A")
        print("Índice de Calinski-Harabasz: N/A")
        print("Índice de Davies-Bouldin: N/A")
    else:
        print(f"Coeficiente de Silueta: {m['silhouette']:.4f}")
        print(f"Índice de Calinski-Harabasz: {m['calinski_harabasz']:.4f}")
        print(f"Índice de Davies-Bouldin: {m['davies_bouldin']:.4f}")

def plot_dbscan(X2d, labels, title, filename):
    """
    Grafica clusters DBSCAN (ruido = -1 con marcador 'x') y guarda figura.
    X2d debe ser 2D (para visualización).
    """
    unique_labels = np.unique(labels)
    plt.figure()
    for lab in unique_labels:
        mask = labels == lab
        if lab == -1:
            plt.scatter(X2d[mask, 0], X2d[mask, 1], s=14, marker='x', label="Ruido (-1)")
        else:
            plt.scatter(X2d[mask, 0], X2d[mask, 1], s=14, label=f"Cluster {lab}")
    plt.title(title)
    plt.xlabel("Componente 1")
    plt.ylabel("Componente 2")
    plt.legend(fontsize=7, ncols=2)
    plt.tight_layout()
    outpath = os.path.join("figs", filename)
    plt.savefig(outpath)
    plt.close()
    print(f"Guardada: {outpath}")

def run_dbscan_dataset(name, X, eps, min_samples, standardize=True, filename_suffix=""):
    """
    Estandariza, ejecuta DBSCAN, imprime métricas y grafica en 2D (usando las 2 primeras features de X).
    """
    Xp = StandardScaler().fit_transform(X) if standardize else X
    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(Xp)

    print(f"\n=== {name} | DBSCAN(eps={eps}, min_samples={min_samples}) ===")
    m = compute_metrics(Xp, labels)
    print(f"Clusters detectados (sin ruido): {m['n_clusters']}  |  Puntos de ruido: {m['n_noise']}")
    print_metrics_es(m)

    X2d = Xp[:, :2]  # para visualización
    plot_dbscan(X2d, labels, f"{name} — DBSCAN", f"dbscan_{filename_suffix}.png")

# --------------------------
# 1) IRIS (pétalo largo/ancho)
# --------------------------
iris = load_iris()
X_iris = iris.data[:, [2, 3]]  # petal length, petal width
run_dbscan_dataset(
    name="Iris (pétalo largo/ancho)",
    X=X_iris,
    eps=0.30,
    min_samples=5,
    standardize=True,
    filename_suffix="iris"
)

# -----------------------------------
# 2) MALL CUSTOMERS (ingreso vs gasto)
# -----------------------------------
def load_mall_customers_X(path_candidates=("Mall_Customers.csv", "mall_customers.csv")):
    """
    Intenta leer 'Mall Customers' y devolver X = [Annual Income (k$), Spending Score (1-100)].
    Si no lo encuentra, crea un dataset sintético similar.
    """
    try:
        import pandas as pd
        for p in path_candidates:
            if os.path.exists(p):
                df = pd.read_csv(p)
                cols = df.columns.str.lower().str.strip()
                df.columns = cols

                income_col = None
                spend_col = None
                for c in df.columns:
                    if "annual" in c and "income" in c:
                        income_col = c
                    if "spending" in c and ("score" in c or "1-100" in c or "1–100" in c):
                        spend_col = c

                if income_col is None or spend_col is None:
                    if "annual income (k$)" in df.columns and "spending score (1-100)" in df.columns:
                        income_col = "annual income (k$)"
                        spend_col = "spending score (1-100)"
                    else:
                        raise ValueError("No se encontraron columnas de ingreso y score de gasto.")

                X = df[[income_col, spend_col]].to_numpy(dtype=float)
                print(f"Se cargó '{p}' correctamente (columnas: '{income_col}', '{spend_col}').")
                return X

        raise FileNotFoundError("No se encontró Mall_Customers.csv")

    except Exception as e:
        print(f"ADVERTENCIA: {e}")
        print("Generando dataset sintético tipo 'Mall Customers' (ingreso vs. score de gasto)...")
        rng = np.random.RandomState(42)
        centers = np.array([
            [30, 20],  # bajo ingreso - bajo gasto
            [30, 80],  # bajo ingreso - alto gasto
            [60, 50],  # ingreso medio - gasto medio
            [90, 20],  # alto ingreso - bajo gasto
            [90, 80],  # alto ingreso - alto gasto
        ])
        Xsyn = np.vstack([
            rng.multivariate_normal(mean=centers[i], cov=[[25, 0], [0, 25]], size=100)
            for i in range(len(centers))
        ])
        return Xsyn

X_mall = load_mall_customers_X()
run_dbscan_dataset(
    name="Mall Customers (Ingreso vs Gasto)",
    X=X_mall,
    eps=0.25,
    min_samples=5,
    standardize=True,
    filename_suffix="mall"
)

# --------------------------
# 3) MOONS (no convexos)
# --------------------------
X_moons, y_moons = make_moons(n_samples=800, noise=0.05, random_state=42)
run_dbscan_dataset(
    name="Moons",
    X=X_moons,
    eps=0.25,
    min_samples=5,
    standardize=True,
    filename_suffix="moons"
)

# --------------------------
# 4) BLOBS (clusters esféricos)
# --------------------------
X_blobs, y_blobs = make_blobs(
    n_samples=600,
    centers=4,
    cluster_std=[0.60, 0.50, 0.60, 0.55],
    random_state=42
)
run_dbscan_dataset(
    name="Blobs (4 centros)",
    X=X_blobs,
    eps=0.25,       # ajusta entre 0.22–0.30 si ves unión/exceso de ruido
    min_samples=5,
    standardize=True,
    filename_suffix="blobs"
)

print("\nListo. Revisa la carpeta ./figs para las imágenes y esta consola para las métricas.")
