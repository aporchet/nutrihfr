"""
Calcul des apports nutritionnels.

Formule (annexe C) :  apport_ligne = quantite_g / 100 x valeur_pour_100g
Agrégation       :  somme par journée, puis MOYENNE DES JOURS par individu
                    (= apport journalier moyen observé de l'individu).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


class IntakeCalculator:
    def __init__(self, tables: dict[str, pd.DataFrame]):
        self.t = tables
        self.nutrients = [n for n in C.NUTRIENTS
                          if n in set(tables["composition"]["code_nutriment"])]
        self.compo_wide = tables["composition"].pivot_table(
            index="code_aliment", columns="code_nutriment", values="valeur_100g")[self.nutrients]

    # -- niveau ligne de consommation -----------------------------------------
    def line_intakes(self) -> pd.DataFrame:
        co = self.t["consommations"].merge(self.compo_wide, left_on="code_aliment",
                                           right_index=True, how="left")
        for n in self.nutrients:
            co[n] = co["quantite_g"] / 100 * co[n]
        return co.merge(self.t["aliments"][["code_aliment", "groupe"]], how="left")

    # -- niveau journée ------------------------------------------------------
    def daily_intakes(self, lines: pd.DataFrame | None = None) -> pd.DataFrame:
        lines = self.line_intakes() if lines is None else lines
        # min_count=1 : une journée sans valeur reste NaN (et pas 0 par erreur)
        day = lines.groupby(["id_indiv", "id_jour"])[self.nutrients].sum(min_count=1)
        return day.reset_index()

    # -- niveau individu -----------------------------------------------------
    def individual_intakes(self, daily: pd.DataFrame | None = None) -> pd.DataFrame:
        daily = self.daily_intakes() if daily is None else daily
        ind = daily.groupby("id_indiv")[self.nutrients].mean().reset_index()
        return self.t["individus"].merge(ind, on="id_indiv", how="inner")

    # -- contributeurs (Q5) : ratio des moyennes pondéré -----------------------
    @staticmethod
    def contributions(lines: pd.DataFrame, individus: pd.DataFrame, nutrient: str,
                      by: str = "groupe", weight: str = "poids_enquete") -> pd.DataFrame:
        """Part (%) de chaque groupe dans l'apport TOTAL de la population.
        = sum_i w_i * apport_i,groupe / sum_i w_i * apport_i,total   (ratio des moyennes)."""
        n_days = individus.set_index("id_indiv")["n_jours"]
        w = individus.set_index("id_indiv")[weight]
        per = lines.groupby(["id_indiv", by])[nutrient].sum().unstack(fill_value=0)
        per = per.div(n_days.reindex(per.index), axis=0)       # apport moyen / jour
        ww = w.reindex(per.index)
        tot = (per.mul(ww, axis=0)).sum()
        out = (100 * tot / tot.sum()).sort_values(ascending=False).rename("contribution_pct")
        return out.reset_index()

    @staticmethod
    def contributions_mean_of_ratios(lines, individus, nutrient, by="groupe",
                                     weight="poids_enquete") -> pd.DataFrame:
        """Moyenne des ratios (pour comparaison/justification) : chaque individu
        pèse autant, quel que soit son niveau d'apport."""
        per = lines.groupby(["id_indiv", by])[nutrient].sum().unstack(fill_value=0)
        share = per.div(per.sum(axis=1).replace(0, np.nan), axis=0)
        w = individus.set_index("id_indiv")[weight].reindex(share.index)
        ok = share.notna().all(axis=1)
        m = (share[ok].mul(w[ok], axis=0)).sum() / w[ok].sum() * 100
        return m.sort_values(ascending=False).rename("contribution_pct").reset_index()


# --------------------------------------------------------------------------
# Densité nutritionnelle (Q4)
# --------------------------------------------------------------------------
def add_density(df: pd.DataFrame, nutrients: list[str]) -> pd.DataFrame:
    """Apport pour 1000 kcal + part de l'énergie apportée par les macronutriments."""
    out = df.copy()
    e = out["energie_kcal"].replace(0, np.nan)
    for n in nutrients:
        if n != "energie_kcal":
            out[f"{n}_per1000kcal"] = out[n] / e * 1000
    for n, k in (("proteines_g", 4), ("glucides_g", 4), ("lipides_g", 9)):
        if n in out:
            out[f"pct_ae_{n.split('_')[0]}"] = 100 * k * out[n] / e
    return out


# --------------------------------------------------------------------------
# Sous-déclaration : critère de Goldberg (Black 2000)
# --------------------------------------------------------------------------
# Équations de Schofield (FAO/OMS/UNU 1985), poids en kg -> kcal/j
SCHOFIELD = {
    ("Homme", 18, 30): (15.3, 679), ("Homme", 30, 60): (11.6, 879), ("Homme", 60, 200): (13.5, 487),
    ("Femme", 18, 30): (14.7, 496), ("Femme", 30, 60): (8.7, 829), ("Femme", 60, 200): (10.5, 596),
}


def bmr_schofield(sexe: str, age: float, poids: float) -> float:
    if pd.isna(poids) or pd.isna(age) or sexe not in ("Homme", "Femme"):
        return np.nan
    for (s, a0, a1), (a, b) in SCHOFIELD.items():
        if s == sexe and a0 <= age < a1:
            return a * poids + b
    return np.nan


def goldberg_cutoff(n_days: int, p=C.GOLDBERG) -> float:
    """Seuil bas EI/BMR (Black 2000) pour un individu observé n_days jours."""
    s = np.sqrt(p["cv_wei"] ** 2 / n_days + p["cv_wb"] ** 2 + p["cv_tp"] ** 2)
    return p["pal"] * np.exp(p["sd_min"] * (s / 100) / np.sqrt(1))


def flag_underreporters(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bmr_kcal"] = [bmr_schofield(s, a, w) for s, a, w in
                       zip(out["sexe"], out["age"], out["poids_kg"])]
    out["ei_bmr"] = out["energie_kcal"] / out["bmr_kcal"]
    out["seuil_goldberg"] = out["n_jours"].map(lambda d: goldberg_cutoff(int(d)))
    out["sous_declarant"] = (out["ei_bmr"] < out["seuil_goldberg"]).astype("boolean")
    out.loc[out["ei_bmr"].isna(), "sous_declarant"] = pd.NA   # poids manquant : inclassable
    return out


def atwater_energy(compo_wide: pd.DataFrame) -> pd.Series:
    """Énergie recalculée (kcal/100 g) à partir des macronutriments."""
    e = 0
    for n, k in C.ATWATER.items():
        if n in compo_wide:
            e = e + compo_wide[n].fillna(0) * k
    return e
