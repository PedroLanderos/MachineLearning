# fastica_plots.py
# Genera proyecciones 2D con FastICA para Digits, Wine e Iris y guarda las figuras en ./figs/

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits, load_wine, load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FastICA

plt.rcParams["figure.dpi"] = 140
os.makedirs("figs", exist_ok=True)

def plot_fastica_2d(X, y, title, filename, class_names=None, random_state=42):
    Xs = StandardScaler().fit_transform(X)
    ica = FastICA(n_components=2, random_state=random_state, max_iter=1000, tol=0.001)
    Z = ica.fit_transform(Xs)

    plt.figure()
    if y is not None:
        classes = np.unique(y)
        for c in classes:
            mask = (y == c)
            label = class_names[c] if class_names is not None and c < len(class_names) else str(c)
            plt.scatter(Z[mask, 0], Z[mask, 1], s=10, alpha=0.8, label=label)
        plt.legend(title="Clases", fontsize=7)
    else:
        plt.scatter(Z[:, 0], Z[:, 1], s=10, alpha=0.8)

    plt.title(title)
    plt.xlabel("ICA 1")
    plt.ylabel("ICA 2")
    plt.tight_layout()
    outpath = os.path.join("figs", filename)
    plt.savefig(outpath)
    plt.close()
    print(f"Guardada: {outpath}")

# Digits (64→2)
digits = load_digits()
plot_fastica_2d(
    X=digits.data,
    y=digits.target,
    title="Digits — FastICA (64→2)",
    filename="fastica_digits.png",
    class_names=[str(i) for i in range(10)]
)

# Wine (13→2)
wine = load_wine()
plot_fastica_2d(
    X=wine.data,
    y=wine.target,
    title="Wine — FastICA (13→2)",
    filename="fastica_wine.png",
    class_names=wine.target_names
)

# Iris (4→2)
iris = load_iris()
plot_fastica_2d(
    X=iris.data,
    y=iris.target,
    title="Iris — FastICA (4→2)",
    filename="fastica_iris.png",
    class_names=iris.target_names
)

print("Listo. Revisa la carpeta ./figs para las imágenes de FastICA.")
