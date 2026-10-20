"""
Statistiques pondérées (pondérations d'enquête INCA).

Choix volontairement simples (niveau junior) et documentés :
- moyenne pondérée  m = sum(w x) / sum(w)
- erreur-type par linéarisation (formule "sandwich" sans prise en compte des
  strates/grappes du plan de sondage -> IC un peu trop étroits ; limite à citer)
- percentiles pondérés par interpolation sur la fonction de répartition pondérée
- régression linéaire pondérée (WLS) avec erreurs-types robustes HC1
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as st


def _clean(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    ok = ~(np.isnan(x) | np.isnan(w))
    return x[ok], w[ok]


def weighted_mean(x, w) -> float:
    x, w = _clean(x, w)
    return float(np.sum(w * x) / np.sum(w)) if len(x) else np.nan


def weighted_se(x, w) -> float:
    x, w = _clean(x, w)
    n = len(x)
    if n < 2:
        return np.nan
    m = np.sum(w * x) / np.sum(w)
    return float(np.sqrt(n / (n - 1) * np.sum(w ** 2 * (x - m) ** 2)) / np.sum(w))


def weighted_sd(x, w) -> float:
    x, w = _clean(x, w)
    m = np.sum(w * x) / np.sum(w)
    return float(np.sqrt(np.sum(w * (x - m) ** 2) / np.sum(w)))


def weighted_quantile(x, w, q):
    x, w = _clean(x, w)
    if not len(x):
        return np.full(np.size(q), np.nan)
    idx = np.argsort(x)
    x, w = x[idx], w[idx]
    cw = (np.cumsum(w) - 0.5 * w) / np.sum(w)
    return np.interp(q, cw, x)


def describe_weighted(df: pd.DataFrame, var: str, weight: str = "poids_enquete",
                      by: list[str] | str | None = None, alpha: float = 0.05) -> pd.DataFrame:
    """Tableau descriptif pondéré : n, moyenne, IC95%, écart-type, P5..P95."""
    z = st.norm.ppf(1 - alpha / 2)

    def one(g):
        x, w = g[var], g[weight]
        m, se = weighted_mean(x, w), weighted_se(x, w)
        p = weighted_quantile(x, w, [0.05, 0.25, 0.5, 0.75, 0.95])
        return pd.Series({"n": int(x.notna().sum()), "moyenne": m,
                          "ic95_bas": m - z * se, "ic95_haut": m + z * se,
                          "ecart_type": weighted_sd(x, w), "P5": p[0], "P25": p[1],
                          "mediane": p[2], "P75": p[3], "P95": p[4]})

    if by is None:
        return one(df).to_frame().T
    rows = {k: one(g) for k, g in df.groupby(by, observed=True)}
    out = pd.DataFrame(rows).T
    out.index.names = [by] if isinstance(by, str) else by
    return out.reset_index()


def unweighted_describe(df, var, by=None):
    tmp = df.assign(_w=1.0)
    return describe_weighted(tmp, var, "_w", by)


def wls(df: pd.DataFrame, y: str, X: list[str], weight: str = "poids_enquete") -> pd.DataFrame:
    """Régression linéaire pondérée. Les variables catégorielles de X sont
    codées en indicatrices (modalité de référence = première par ordre alphabétique)."""
    d = df[[y, weight] + X].dropna()
    Xd = pd.get_dummies(d[X], drop_first=True, dtype=float)
    Xd.insert(0, "constante", 1.0)
    Xm, yv, w = Xd.to_numpy(float), d[y].to_numpy(float), d[weight].to_numpy(float)
    w = w / w.mean()
    XtW = Xm.T * w
    bread = np.linalg.inv(XtW @ Xm)
    beta = bread @ XtW @ yv
    e = yv - Xm @ beta
    n, k = Xm.shape
    meat = (Xm.T * (w * e) ** 2) @ Xm
    cov = bread @ meat @ bread * n / (n - k)            # HC1
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * st.t.sf(np.abs(t), n - k)
    r2 = 1 - np.sum(w * e ** 2) / np.sum(w * (yv - np.average(yv, weights=w)) ** 2)
    out = pd.DataFrame({"coef": beta, "erreur_type": se, "t": t, "p_value": p,
                        "ic95_bas": beta - 1.96 * se, "ic95_haut": beta + 1.96 * se},
                       index=Xd.columns)
    out.attrs.update({"n": n, "r2_pondere": r2})
    return out


def weighted_mean_diff_test(df, var, group_col, weight="poids_enquete"):
    """Différence de moyennes pondérées entre 2 groupes (test z, linéarisation)."""
    g = [x for _, x in df.groupby(group_col)]
    if len(g) != 2:
        raise ValueError("2 groupes attendus")
    m = [weighted_mean(x[var], x[weight]) for x in g]
    se = [weighted_se(x[var], x[weight]) for x in g]
    d, s = m[0] - m[1], np.sqrt(se[0] ** 2 + se[1] ** 2)
    keys = list(df.groupby(group_col).groups)
    return {"groupe_1": keys[0], "groupe_2": keys[1], "difference": d,
            "ic95_bas": d - 1.96 * s, "ic95_haut": d + 1.96 * s,
            "p_value": 2 * st.norm.sf(abs(d / s))}


def variance_components(daily: pd.DataFrame, var: str) -> dict:
    """Décomposition intra / inter-individuelle (ANOVA à un facteur aléatoire).
    s2_intra = variance moyenne d'un jour à l'autre au sein d'un individu
    s2_inter = variance des moyennes individuelles - s2_intra / nb moyen de jours."""
    g = daily.groupby("id_indiv")[var]
    k = g.count()
    g = daily[daily["id_indiv"].isin(k[k >= 2].index)].groupby("id_indiv")[var]
    s2_w = g.var(ddof=1).mean()
    n_bar = g.count().mean()
    s2_b = max(g.mean().var(ddof=1) - s2_w / n_bar, 0)
    return {"variance_intra": s2_w, "variance_inter": s2_b,
            "ratio_intra_inter": s2_w / s2_b if s2_b > 0 else np.nan,
            "part_inter_pct": 100 * s2_b / (s2_b + s2_w), "n_individus": int(g.ngroups),
            "n_jours_moyen": n_bar}
