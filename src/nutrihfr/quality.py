"""
Contrôle qualité (8 dimensions de l'annexe B) et nettoyage.

`QualityChecker` ne modifie rien : il mesure et produit un rapport.
`DataCleaner` applique ensuite des règles simples et documentées, et garde la
trace de chaque ligne écartée (table `exclusions`) -> traçabilité.
"""
from __future__ import annotations

import pandas as pd

from . import config as C

# Quantité maximale plausible pour UNE prise alimentaire (g). Au-delà : erreur
# de saisie probable. Seuil plus large pour les boissons (on boit 1-2 L d'eau).
MAX_QTY_SOLID = 1500
MAX_QTY_DRINK = 3000
DRINK_KEYWORDS = ("eau", "boisson", "jus", "lait", "soda", "café", "thé", "bière", "vin", "soupe")


def _is_drink(groupe: pd.Series) -> pd.Series:
    g = groupe.fillna("").astype(str).str.lower()
    return g.apply(lambda x: any(k in x for k in DRINK_KEYWORDS))


class QualityChecker:
    def __init__(self, tables: dict[str, pd.DataFrame]):
        self.t = tables
        self.rows: list[dict] = []

    def _add(self, dimension, table, controle, valeur, statut, detail=""):
        self.rows.append({"dimension": dimension, "table": table, "controle": controle,
                          "resultat": valeur, "statut": statut, "detail": detail})

    # 1. Complétude ---------------------------------------------------------
    def completeness(self):
        for name in ("individus", "consommations", "composition"):
            df = self.t[name]
            for col in df.columns:
                pct = 100 * df[col].isna().mean()
                if pct > 0 or col in ("poids_kg", "taille_cm", "poids_enquete", "quantite_g"):
                    statut = "OK" if pct == 0 else ("ALERTE" if pct < 5 else "KO")
                    self._add("Complétude", name, f"% manquants {col}", f"{pct:.2f} %", statut)

    # 2. Unicité --------------------------------------------------------------
    def uniqueness(self):
        n = int(self.t["individus"]["id_indiv"].duplicated().sum())
        self._add("Unicité", "individus", "id_indiv en double", n, "OK" if n == 0 else "KO")
        d = int(self.t["consommations"]["doublon_exact"].sum())
        self._add("Unicité", "consommations", "lignes strictement identiques", d,
                  "OK" if d == 0 else "ALERTE", "même individu/jour/aliment/quantité")
        n = int(self.t["aliments"]["code_aliment"].duplicated().sum())
        self._add("Unicité", "aliments", "code_aliment en double", n, "OK" if n == 0 else "KO")

    # 3. Validité -------------------------------------------------------------
    def validity(self):
        ind, co = self.t["individus"], self.t["consommations"]
        n = int((ind["age"] < 0).sum())
        self._add("Validité", "individus", "âge < 0", n, "OK" if n == 0 else "KO")
        n = int((co["quantite_g"] < 0).sum())
        self._add("Validité", "consommations", "quantité < 0", n, "OK" if n == 0 else "KO")
        n = int((co["quantite_g"] == 0).sum())
        self._add("Validité", "consommations", "quantité = 0", n, "OK" if n == 0 else "ALERTE")
        n = int((ind["poids_enquete"] <= 0).sum())
        self._add("Validité", "individus", "pondération <= 0", n, "OK" if n == 0 else "KO")
        n = int((~ind["sexe"].isin(["Homme", "Femme"])).sum())
        self._add("Validité", "individus", "sexe non codé", n, "OK" if n == 0 else "KO")

    # 4. Cohérence ------------------------------------------------------------
    def consistency(self):
        ind = self.t["individus"]
        nj = ind["n_jours"].fillna(0)
        n = int((nj == 0).sum())
        self._add("Cohérence", "individus", "individus sans journée de consommation", n,
                  "OK" if n == 0 else "ALERTE")
        n = int((nj > 7).sum())
        self._add("Cohérence", "individus", "plus de 7 jours de consommation", n,
                  "OK" if n == 0 else "ALERTE")
        imc = ind["poids_kg"] / (ind["taille_cm"] / 100) ** 2
        n = int(((imc < 13) | (imc > 70)).sum())
        self._add("Cohérence", "individus", "IMC hors [13 ; 70]", n, "OK" if n == 0 else "ALERTE")

    # 5. Intégrité référentielle ---------------------------------------------
    def referential_integrity(self):
        co, al, comp = self.t["consommations"], self.t["aliments"], self.t["composition"]
        unknown = set(co["code_aliment"]) - set(al["code_aliment"])
        self._add("Intégrité référentielle", "consommations", "code_aliment absent de la nomenclature",
                  len(unknown), "OK" if not unknown else "ALERTE", str(sorted(unknown)[:10]))
        cover = 100 * co["code_aliment"].isin(comp["code_aliment"]).mean()
        self._add("Intégrité référentielle", "consommations",
                  "couverture composition (% lignes avec composition)",
                  f"{cover:.2f} %", "OK" if cover > 99 else "ALERTE")
        orphan = set(co["id_indiv"]) - set(self.t["individus"]["id_indiv"])
        self._add("Intégrité référentielle", "consommations", "id_indiv inconnu", len(orphan),
                  "OK" if not orphan else "KO")

    # 6. Exactitude / plausibilité -------------------------------------------
    def plausibility(self):
        co = self.t["consommations"].merge(self.t["aliments"][["code_aliment", "groupe"]],
                                           how="left")
        drink = _is_drink(co["groupe"])
        too_much = ((~drink) & (co["quantite_g"] > MAX_QTY_SOLID)) | \
                   (drink & (co["quantite_g"] > MAX_QTY_DRINK))
        self._add("Exactitude", "consommations",
                  f"quantité > {MAX_QTY_SOLID} g (solide) ou > {MAX_QTY_DRINK} g (boisson)",
                  int(too_much.sum()), "OK" if too_much.sum() == 0 else "ALERTE")
        comp = self.t["composition"]
        wide = comp.pivot_table(index="code_aliment", columns="code_nutriment",
                                values="valeur_100g")
        macro = wide[[c for c in ("proteines_g", "glucides_g", "lipides_g", "fibres_g",
                                  "alcool_g") if c in wide]].sum(axis=1)
        n = int((macro > 105).sum())
        self._add("Exactitude", "composition", "somme des macronutriments > 105 g/100 g", n,
                  "OK" if n == 0 else "ALERTE")

    # 7. Homogénéité ----------------------------------------------------------
    def homogeneity(self):
        known = set(C.NUTRIENTS)
        nut = set(self.t["nutriments"]["code_nutriment"])
        unk = nut - known
        self._add("Homogénéité", "nutriments", "nutriments sans unité connue", len(unk),
                  "OK" if not unk else "KO")
        self._add("Homogénéité", "consommations", "unité des quantités", "g (grammes)", "OK",
                  "toutes les quantités INCA sont en grammes consommés")

    # 8. Traçabilité ----------------------------------------------------------
    def traceability(self, sources: list[dict]):
        for s in sources:
            self._add("Traçabilité", s["table"], f"empreinte {s['fichier']}",
                      s["sha256"][:12], "OK", f"{s['n_lignes']} lignes")

    def run(self, sources: list[dict] | None = None) -> pd.DataFrame:
        self.rows = []
        self.completeness(); self.uniqueness(); self.validity(); self.consistency()
        self.referential_integrity(); self.plausibility(); self.homogeneity()
        if sources:
            self.traceability(sources)
        return pd.DataFrame(self.rows)

    @staticmethod
    def to_markdown(report: pd.DataFrame, title="Data Quality Report") -> str:
        lines = [f"# {title}", "",
                 "Généré automatiquement par `QualityChecker` (src/nutrihfr/quality.py).", "",
                 "| Dimension | Table | Contrôle | Résultat | Statut | Détail |",
                 "|---|---|---|---|---|---|"]
        for r in report.itertuples():
            lines.append(f"| {r.dimension} | {r.table} | {r.controle} | {r.resultat} | "
                         f"{r.statut} | {r.detail} |")
        return "\n".join(lines) + "\n"


class DataCleaner:
    """Règles de nettoyage appliquées APRÈS le contrôle qualité."""

    def __init__(self, tables: dict[str, pd.DataFrame]):
        self.t = {k: v.copy() for k, v in tables.items()}
        self.exclusions: list[pd.DataFrame] = []

    def _exclude(self, mask: pd.Series, reason: str):
        co = self.t["consommations"]
        ex = co[mask].copy()
        ex["motif"] = reason
        self.exclusions.append(ex)
        self.t["consommations"] = co[~mask].reset_index(drop=True)

    def run(self) -> dict[str, pd.DataFrame]:
        co = self.t["consommations"]
        self._exclude(co["doublon_exact"], "doublon exact")
        co = self.t["consommations"]
        self._exclude(co["quantite_g"].isna() | (co["quantite_g"] < 0), "quantité manquante ou négative")
        co = self.t["consommations"].merge(self.t["aliments"][["code_aliment", "groupe"]], how="left")
        drink = _is_drink(co["groupe"])
        too_much = ((~drink) & (co["quantite_g"] > MAX_QTY_SOLID)) | \
                   (drink & (co["quantite_g"] > MAX_QTY_DRINK))
        self._exclude(too_much.to_numpy(), "quantité implausible")
        # aliments hors nomenclature : écartés et listés dans la table d'exceptions
        co = self.t["consommations"]
        unknown = ~co["code_aliment"].isin(self.t["aliments"]["code_aliment"])
        self._exclude(unknown, "aliment absent de la nomenclature (table d'exceptions)")
        self.t["consommations"] = self.t["consommations"].drop(columns="doublon_exact")

        ex = (pd.concat(self.exclusions, ignore_index=True) if self.exclusions
              else pd.DataFrame(columns=["id_conso", "motif"]))
        self.t["exclusions"] = ex.drop(columns=["doublon_exact"], errors="ignore")
        # journées / individus à recalculer après exclusions
        jours = self.t["consommations"]["id_jour"].unique()
        self.t["journees"] = self.t["journees"][self.t["journees"]["id_jour"].isin(jours)]
        nj = self.t["journees"].groupby("id_indiv").size().rename("n_jours")
        ind = self.t["individus"].drop(columns="n_jours").merge(nj.reset_index(), how="left")
        self.t["individus"] = ind[ind["n_jours"].fillna(0) > 0].reset_index(drop=True)
        return self.t

    def summary(self) -> pd.DataFrame:
        ex = self.t.get("exclusions")
        if ex is None or ex.empty:
            return pd.DataFrame(columns=["motif", "n_lignes"])
        return ex.groupby("motif").size().rename("n_lignes").reset_index()
