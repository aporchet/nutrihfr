"""Fonctions statistiques pondérées utilisées dans les analyses.

Simplification assumée : les intervalles de confiance utilisent les pondérations mais
pas les strates/grappes du plan de sondage INCA 3 (ils sont donc un peu trop étroits).
"""
import numpy as np
import pandas as pd


def moyenne_ponderee(x, w):
    return np.sum(w * x) / np.sum(w)


def erreur_type_ponderee(x, w):
    """Erreur-type de la moyenne pondérée (approximation par linéarisation)."""
    x, w = np.asarray(x, float), np.asarray(w, float)
    m = moyenne_ponderee(x, w)
    n = len(x)
    return np.sqrt(n / (n - 1) * np.sum(w**2 * (x - m) ** 2)) / np.sum(w)


def quantile_pondere(x, w, q):
    """Quantile(s) pondéré(s) : interpolation sur la fonction de répartition pondérée."""
    x, w = np.asarray(x, float), np.asarray(w, float)
    ordre = np.argsort(x)
    x, w = x[ordre], w[ordre]
    repartition = (np.cumsum(w) - 0.5 * w) / np.sum(w)
    return np.interp(q, repartition, x)


def resume_pondere(df, variable, par=None, poids="ponderation"):
    """Effectif, moyenne pondérée + IC 95 %, médiane et percentiles pondérés."""
    def resume(d):
        d = d.dropna(subset=[variable])
        x, w = d[variable], d[poids]
        m, se = moyenne_ponderee(x, w), erreur_type_ponderee(x, w)
        p5, p25, p50, p75, p95 = quantile_pondere(x, w, [0.05, 0.25, 0.5, 0.75, 0.95])
        return pd.Series({"n": len(d), "moyenne": m, "ic95_bas": m - 1.96 * se,
                          "ic95_haut": m + 1.96 * se, "P5": p5, "P25": p25,
                          "mediane": p50, "P75": p75, "P95": p95})

    if par is None:
        return resume(df).to_frame().T
    return df.groupby(par, observed=True).apply(resume, include_groups=False).reset_index()


def contributions(lignes, individus, nutriment, par="groupe"):
    """Part (%) de chaque groupe d'aliments dans l'apport total de la population :
    'ratio des moyennes' = somme pondérée des apports du groupe / somme pondérée des apports."""
    poids = individus.set_index("NOIND")["ponderation"]
    lignes = lignes.assign(w=lignes["NOIND"].map(poids))
    total_groupe = (lignes[nutriment] * lignes["w"]).groupby(lignes[par]).sum()
    return (100 * total_groupe / total_groupe.sum()).sort_values(ascending=False)


def regression_ponderee(df, y, variables, poids="ponderation"):
    """Régression linéaire pondérée (moindres carrés pondérés).
    Les variables qualitatives sont transformées en indicatrices (1re modalité = référence)."""
    d = df[[y, poids] + variables].dropna()
    X = pd.get_dummies(d[variables], drop_first=True, dtype=float)
    X.insert(0, "constante", 1.0)
    w = d[poids] / d[poids].mean()
    Xw = X.mul(np.sqrt(w), axis=0)
    yw = d[y] * np.sqrt(w)
    coef, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    residus = yw - Xw @ coef
    sigma2 = residus @ residus / (len(d) - X.shape[1])
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(Xw.T @ Xw)))
    return pd.DataFrame({"coefficient": coef, "ic95_bas": coef - 1.96 * se,
                         "ic95_haut": coef + 1.96 * se}, index=X.columns)


# --- Sous-déclaration : critère de Goldberg ---------------------------------------

def metabolisme_base(sexe, age, poids):
    """Métabolisme de base (kcal/j), équations de Schofield (OMS 1985)."""
    coef = {("Homme", 0): (15.3, 679), ("Homme", 1): (11.6, 879), ("Homme", 2): (13.5, 487),
            ("Femme", 0): (14.7, 496), ("Femme", 1): (8.7, 829), ("Femme", 2): (10.5, 596)}
    tranche = 0 if age < 30 else (1 if age < 60 else 2)
    a, b = coef[(sexe, tranche)]
    return a * poids + b


def seuil_goldberg(n_jours, pal=1.55):
    """Seuil bas du rapport apport énergétique / métabolisme de base (Black, 2000).
    En dessous, l'apport déclaré est incompatible avec le maintien du poids."""
    s = np.sqrt(23.0**2 / n_jours + 8.5**2 + 15.0**2)    # CV intra-apport, CV MB, CV dépense
    return pal * np.exp(-2 * (s / 100))


def variance_intra_inter(jours, nutriment):
    """Part de variance entre individus (inter) et d'un jour à l'autre (intra)."""
    g = jours.groupby("NOIND")[nutriment]
    intra = g.var(ddof=1).mean()
    inter = max(g.mean().var(ddof=1) - intra / g.count().mean(), 0)
    return {"variance_intra": intra, "variance_inter": inter,
            "part_inter_%": 100 * inter / (inter + intra)}
