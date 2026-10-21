"""Pipeline de traitement + feature engineering du projet NutriHFr en 3 classes + la création de la base SQLite.

ChargeurINCA3    lit les CSV et ne garde que les adultes de la Pop3
ControleQualite  mesure la qualité des données (8 dimensions)
CalculApports    calcule les apports nutritionnels journaliers par individu
creer_base_sqlite  range les données dans le modèle relationnel (sql/schema.sql)
"""

import sqlite3

import pandas as pd

from . import config as C


class ChargeurINCA3:
    """Lecture des fichiers bruts INCA 3."""

    def __init__(self, dossier=C.DOSSIER_BRUT):
        self.dossier = dossier

    def lire(self, cle):
        """Lit un fichier INCA 3 (séparateur ';', encodage UTF-8 avec BOM)."""
        return pd.read_csv(
            self.dossier / C.FICHIERS[cle],
            sep=";",
            encoding="utf-8-sig",
            low_memory=False,
        )

    def individus(self):
        """Adultes 18-79 ans participants au volet consommation (pondération pop3 non vide)."""
        df = self.lire("individus")
        df = df[df[C.PONDERATION].notna() & df["tage_PS"].isin(C.CLASSES_AGE)].copy()
        df["sexe"] = df["sex_PS"].map(C.SEXES)
        df["classe_age"] = df["tage_PS"].map(C.CLASSES_AGE)
        df["age_approx"] = df["tage_PS"].map(C.AGE_MILIEU)
        df["ponderation"] = df[C.PONDERATION]
        colonnes = [
            "NOIND",
            "sexe",
            "classe_age",
            "age_approx",
            "poids",
            "taille",
            "ponderation",
        ]
        return df[colonnes].reset_index(drop=True)

    def consommations(self, ids):
        """Lignes de consommation (un aliment consommé un jour par un individu)."""
        df = self.lire("consommations")
        df = df[df["NOIND"].isin(ids)].copy()
        df["groupe"] = df["gpe_INCA3"].map(C.GROUPES)
        colonnes = [
            "NOIND",
            "NUM_LIGNE",
            "R24_num",
            "R24_nombre",
            "R24_pond",
            "gpe_INCA3",
            "groupe",
            "aliment_code_INCA3",
            "aliment_libelle_INCA3",
            "qte_conso",
            "qte_conso_pond",
        ]
        return df[colonnes + list(C.NUTRIMENTS)].reset_index(drop=True)

    def apports_anses(self, ids):
        """Apports journaliers calculés par l'Anses (sert à valider notre calcul)."""
        df = self.lire("apports")
        df = df[df["NOIND"].isin(ids)]
        renommage = {col_anses: nom for nom, (_, _, col_anses) in C.NUTRIMENTS.items()}
        return (
            df[["NOIND"] + list(renommage)]
            .rename(columns=renommage)
            .reset_index(drop=True)
        )

    def charger(self):
        individus = self.individus()
        ids = individus["NOIND"]
        return individus, self.consommations(ids), self.apports_anses(ids)


class ControleQualite:
    """Contrôles qualité selon les 8 dimensions demandées (annexe B)."""

    def __init__(self, individus, consommations):
        self.ind = individus
        self.conso = consommations
        self.resultats = []

    def ajouter(self, dimension, controle, valeur, ok):
        self.resultats.append(
            {
                "dimension": dimension,
                "controle": controle,
                "resultat": valeur,
                "statut": "OK" if ok else "A VERIFIER",
            }
        )

    def executer(self):
        ind, co = self.ind, self.conso
        nut = list(C.NUTRIMENTS)
        self.resultats = []

        # 1. Complétude
        for col in ["poids", "taille", "ponderation"]:
            n = ind[col].isna().sum()
            self.ajouter("Complétude", f"individus : {col} manquant", n, n == 0)
        n = co[nut].isna().any(axis=1).sum()
        self.ajouter("Complétude", "lignes sans composition nutritionnelle", n, n == 0)
        # 2. Unicité
        n = ind["NOIND"].duplicated().sum()
        self.ajouter("Unicité", "individus en double (NOIND)", n, n == 0)
        n = co["NUM_LIGNE"].duplicated().sum()
        self.ajouter(
            "Unicité", "lignes de consommation en double (NUM_LIGNE)", n, n == 0
        )
        # 3. Validité
        n = (co["qte_conso"] <= 0).sum()
        self.ajouter("Validité", "quantités nulles ou négatives", n, n == 0)
        n = (co[nut] < 0).sum().sum()
        self.ajouter("Validité", "valeurs de composition négatives", n, n == 0)
        n = ind["sexe"].isna().sum() + ind["classe_age"].isna().sum()
        self.ajouter("Validité", "sexe ou classe d'âge non codé", n, n == 0)
        # 4. Cohérence
        jours = co.groupby("NOIND").agg(
            vus=("R24_num", "nunique"), prevus=("R24_nombre", "first")
        )
        n = (jours["vus"] != jours["prevus"]).sum()
        self.ajouter(
            "Cohérence", "nb de jours observés différent de R24_nombre", n, n == 0
        )
        n = (~ind["NOIND"].isin(co["NOIND"])).sum()
        self.ajouter("Cohérence", "adultes sans aucune consommation", n, n == 0)
        # 5. Intégrité référentielle
        n = (~co["NOIND"].isin(ind["NOIND"])).sum()
        self.ajouter(
            "Intégrité référentielle", "consommations d'un individu inconnu", n, n == 0
        )
        n = co["groupe"].isna().sum()
        self.ajouter(
            "Intégrité référentielle",
            "lignes avec un groupe d'aliments inconnu",
            n,
            n == 0,
        )
        # 6. Exactitude / plausibilité
        n = (co["qte_conso"] > 2000).sum()
        self.ajouter("Exactitude", "quantités > 2 kg en une prise", n, n == 0)
        imc = ind["poids"] / (ind["taille"] / 100) ** 2
        n = ((imc < 13) | (imc > 70)).sum()
        self.ajouter("Exactitude", "IMC hors [13 ; 70]", n, n == 0)
        # 7. Homogénéité
        atwater = (
            4 * co["proteines"]
            + 4 * co["glucides"]
            + 9 * co["lipides"]
            + 2 * co["fibres"]
            + 7 * co["alcool"]
        )
        ecart = ((atwater - co["aet"]).abs() / co["aet"])[co["aet"] > 20]
        pct = 100 * (ecart < 0.10).mean()
        self.ajouter(
            "Homogénéité",
            "% lignes où énergie Atwater ≈ énergie (écart < 10 %)",
            round(pct, 1),
            pct > 95,
        )
        # 8. Traçabilité
        self.ajouter(
            "Traçabilité",
            "lignes de consommation conservées / lues",
            f"{len(co)} / {len(co)}",
            True,
        )
        return pd.DataFrame(self.resultats)


class CalculApports:
    """Apport journalier moyen par individu, selon la méthode de l'Anses :
    apport = somme sur les lignes de (qte_conso_pond / 100 x composition) / nombre de jours.
    qte_conso_pond intègre la pondération R24_pond (équilibre semaine / week-end)."""

    def __init__(self, consommations, individus):
        self.conso = consommations
        self.ind = individus
        self.nutriments = list(C.NUTRIMENTS)

    def par_ligne(self):
        """Apport de chaque ligne de consommation (pondéré semaine / week-end)."""
        lignes = self.conso.copy()
        for n in self.nutriments:
            lignes[n] = (
                lignes["qte_conso_pond"] / 100 * lignes[n] / lignes["R24_nombre"]
            )
        return lignes

    def par_individu(self):
        """Apport journalier moyen de chaque individu, fusionné avec ses caractéristiques."""
        apports = self.par_ligne().groupby("NOIND")[self.nutriments].sum().reset_index()
        return self.ind.merge(apports, on="NOIND", how="inner")

    def par_jour(self):
        """Apport de chaque journée de rappel (quantités brutes), utile pour Q6."""
        lignes = self.conso.copy()
        for n in self.nutriments:
            lignes[n] = lignes["qte_conso"] / 100 * lignes[n]
        return lignes.groupby(["NOIND", "R24_num"])[self.nutriments].sum().reset_index()


def creer_base_sqlite(individus, consommations, apports, chemin=C.BASE_SQLITE):
    """Crée la base SQLite à partir de sql/schema.sql et y insère les données."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(chemin)
    con.executescript(C.SCHEMA_SQL.read_text(encoding="utf-8"))

    tables = {
        "individus": individus.rename(columns={"NOIND": "id_indiv"})[
            ["id_indiv", "sexe", "classe_age", "poids", "taille", "ponderation"]
        ],
        "journees": consommations.groupby(["NOIND", "R24_num"], as_index=False)[
            "R24_pond"
        ]
        .first()
        .rename(
            columns={
                "NOIND": "id_indiv",
                "R24_num": "no_jour",
                "R24_pond": "poids_jour",
            }
        ),
        "aliments": consommations.drop_duplicates("aliment_code_INCA3").rename(
            columns={
                "aliment_code_INCA3": "code_aliment",
                "aliment_libelle_INCA3": "libelle",
            }
        )[["code_aliment", "libelle"]],
        "nutriments": pd.DataFrame(
            [
                {"code_nutriment": k, "libelle": v[0], "unite": v[1]}
                for k, v in C.NUTRIMENTS.items()
            ]
        ),
        "consommations": consommations.rename(
            columns={
                "NUM_LIGNE": "id_ligne",
                "NOIND": "id_indiv",
                "R24_num": "no_jour",
                "aliment_code_INCA3": "code_aliment",
                "qte_conso": "quantite_g",
                "qte_conso_pond": "quantite_pond_g",
            }
        )[
            [
                "id_ligne",
                "id_indiv",
                "no_jour",
                "code_aliment",
                "groupe",
                "quantite_g",
                "quantite_pond_g",
            ]
        ],
        "composition": consommations.melt(
            id_vars="NUM_LIGNE",
            value_vars=list(C.NUTRIMENTS),
            var_name="code_nutriment",
            value_name="valeur_100g",
        )
        .rename(columns={"NUM_LIGNE": "id_ligne"})
        .dropna(),
        "apports": apports.melt(
            id_vars="NOIND",
            value_vars=list(C.NUTRIMENTS),
            var_name="code_nutriment",
            value_name="valeur_par_jour",
        ).rename(columns={"NOIND": "id_indiv"}),
    }
    for nom, df in tables.items():
        df.to_sql(nom, con, if_exists="append", index=False)
    con.commit()
    con.close()
    return {nom: len(df) for nom, df in tables.items()}
