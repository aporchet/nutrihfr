"""Style graphique commun (matplotlib) : une seule palette, couleurs fixes par entité."""
from __future__ import annotations

import matplotlib.pyplot as plt

from . import config as C

# Palette catégorielle (ordre fixe, validée pour le daltonisme) - 8 couleurs max.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
OTHER = "#b5b4ad"            # gris pour "Autres"
SEX_COLORS = {"Homme": PALETTE[0], "Femme": PALETTE[1]}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def set_style():
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 150, "figure.facecolor": "white",
        "axes.facecolor": "white", "axes.edgecolor": GRID, "axes.labelcolor": INK2,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.axisbelow": True, "xtick.color": INK2, "ytick.color": INK2,
        "legend.frameon": False, "font.size": 10,
        "axes.prop_cycle": plt.cycler(color=PALETTE),
    })


def savefig(fig, name: str):
    C.FIGURES.mkdir(parents=True, exist_ok=True)
    path = C.FIGURES / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    return path


def top_n_with_other(s, n=7, label="Autres"):
    """Garde les n premières catégories et regroupe le reste dans 'Autres'
    (au-delà de 8 couleurs, un graphique n'est plus lisible)."""
    s = s.sort_values(ascending=False)
    out = s.iloc[:n].copy()
    if len(s) > n:
        out[label] = s.iloc[n:].sum()
    return out
