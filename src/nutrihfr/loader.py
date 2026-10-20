"""
Chargement des données brutes et mise au format canonique.

- `read_csv_robust`  : lit un CSV en détectant encodage et séparateur.
- `Inca3Loader`      : INCA 3 -> tables individus / journees / consommations /
                       aliments / nutriments / composition (+ apports fournis).
- `Inca2Loader`      : INCA 2 -> individus + apports fournis (bonus comparaison).
- `CiqualLoader`     : table Ciqual -> composition pour 100 g (valeurs texte nettoyées).

Chaque loader garde un journal (`self.log`) de ce qu'il a fait : fichier, empreinte
SHA-256, nombre de lignes, colonnes renommées. C'est la base de la traçabilité.
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C


# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------
def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_robust(path: Path, **kwargs) -> pd.DataFrame:
    """Lit un CSV français : essaie utf-8 puis latin-1, devine le séparateur,
    gère la virgule décimale."""
    path = Path(path)
    if path.suffix.lower() in (".xls", ".xlsx"):
        return pd.read_excel(path, **kwargs)
    last_err = None
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                sample = f.read(20000)
            sep = csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
            return pd.read_csv(path, sep=sep, encoding=enc, decimal="," if sep == ";" else ".",
                               low_memory=False, **kwargs)
        except (UnicodeDecodeError, csv.Error) as e:
            last_err = e
    raise ValueError(f"Impossible de lire {path} : {last_err}")


def to_number(s: pd.Series) -> pd.Series:
    """Convertit une colonne en nombre en gérant les écritures Ciqual :
    'traces' -> 0, '< 0,5' -> 0,25 (moitié du seuil), '-' ou vide -> NaN."""
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)

    def conv(v):
        if pd.isna(v):
            return np.nan
        t = str(v).strip().lower().replace(",", ".")
        if t in ("", "-", "nd", "na"):
            return np.nan
        if t == "traces":
            return 0.0
        m = re.match(r"^<\s*([0-9.]+)$", t)
        if m:
            return float(m.group(1)) / 2
        try:
            return float(t)
        except ValueError:
            return np.nan

    return s.map(conv).astype(float)


def rename_existing(df: pd.DataFrame, mapping: dict, table: str, log: list) -> pd.DataFrame:
    """Renomme les colonnes présentes ; signale celles qui manquent (sans planter)."""
    missing = [c for c in mapping if c not in df.columns]
    if missing:
        log.append({"etape": "renommage", "table": table,
                    "detail": f"colonnes absentes du fichier : {missing}"})
    present = {k: v for k, v in mapping.items() if k in df.columns}
    return df.rename(columns=present)


def suggest_columns(df: pd.DataFrame, keywords: list[str]) -> dict:
    """Aide au paramétrage : pour chaque mot-clé, liste les colonnes qui le contiennent."""
    return {k: [c for c in df.columns if k.lower() in c.lower()] for k in keywords}


def age_class(age: pd.Series) -> pd.Series:
    return pd.cut(age, bins=C.AGE_BINS, labels=C.AGE_LABELS, right=False).astype(str)


# --------------------------------------------------------------------------
# INCA 3
# --------------------------------------------------------------------------
class Inca3Loader:
    survey = "INCA3"

    def __init__(self, raw_dir: Path | None = None):
        self.raw_dir = Path(raw_dir) if raw_dir else C.raw_dir("inca3")
        self.log: list[dict] = []
        self.sources: list[dict] = []

    def _read(self, key: str) -> pd.DataFrame:
        path = self.raw_dir / C.INCA3_FILES[key]
        df = read_csv_robust(path)
        self.sources.append({"enquete": self.survey, "table": key, "fichier": path.name,
                             "sha256": file_sha256(path), "n_lignes": len(df),
                             "n_colonnes": df.shape[1]})
        return df

    def load(self) -> dict[str, pd.DataFrame]:
        cols = C.INCA3_COLS
        raw_indiv = self._read("indiv")
        raw_conso = self._read("conso")
        raw_apports = self._read("apports")
        raw_nomen = self._read("nomenclature")

        # --- individus ------------------------------------------------------
        ind = rename_existing(raw_indiv, cols["indiv"], "indiv", self.log)
        keep = [c for c in cols["indiv"].values() if c in ind.columns]
        ind = ind[keep].copy()
        ind["enquete"] = self.survey
        ind["sexe"] = ind["sexe"].map(C.SEX_CODES)
        if "age" not in ind.columns and "classe_age_src" in ind.columns and C.AGE_FROM_CLASS:
            ind["age"] = ind["classe_age_src"].map(C.AGE_FROM_CLASS)
            self.log.append({"etape": "age", "table": "individus",
                             "detail": "âge approximé par le milieu de classe"})
        for c in ("age", "poids_kg", "taille_cm", "poids_enquete"):
            if c in ind.columns:
                ind[c] = to_number(ind[c])
        n0 = len(ind)
        ind = ind[ind["age"].between(C.AGE_MIN, C.AGE_MAX) & ind["poids_enquete"].notna()]
        self.log.append({"etape": "filtre_population", "table": "individus",
                         "detail": f"adultes {C.AGE_MIN}-{C.AGE_MAX} ans avec pondération : "
                                   f"{n0} -> {len(ind)}"})
        ind["classe_age"] = age_class(ind["age"])

        # --- consommations ---------------------------------------------------
        co = rename_existing(raw_conso, cols["conso"], "conso", self.log)
        co = rename_existing(co, cols["conso_nutrients"], "conso", self.log)
        co = co[co["id_indiv"].isin(ind["id_indiv"])].copy()
        # doublon = ligne strictement identique sur TOUTES les colonnes brutes
        co["doublon_exact"] = co.duplicated(keep="first")
        co["quantite_g"] = to_number(co["quantite_g"])
        co["id_jour"] = co["id_indiv"].astype(str) + "_" + co["no_jour"].astype(str)
        co = co.reset_index(drop=True)
        co["id_conso"] = np.arange(1, len(co) + 1)

        # --- aliments (nomenclature) ----------------------------------------
        al = rename_existing(raw_nomen, cols["nomenclature"], "nomenclature", self.log)
        al = al[["code_aliment", "libelle", "groupe"]].drop_duplicates("code_aliment")

        # --- composition (pour 100 g) extraite de conso-compo-alim ------------
        nut = [n for n in cols["conso_nutrients"].values() if n in co.columns]
        tmp = co[["code_aliment", "quantite_g"] + nut].copy()
        for n in nut:
            tmp[n] = to_number(tmp[n])
            if C.COMPO_EMBARQUEE_PAR == "portion":
                tmp[n] = tmp[n] / tmp["quantite_g"].where(tmp["quantite_g"] > 0) * 100
        compo_wide = tmp.groupby("code_aliment")[nut].median()
        compo = (compo_wide.reset_index()
                 .melt(id_vars="code_aliment", var_name="code_nutriment", value_name="valeur_100g"))
        compo["source"] = "INCA3 conso-compo-alim"

        nutriments = pd.DataFrame([{"code_nutriment": k, "libelle": v[0], "unite": v[1]}
                                   for k, v in C.NUTRIENTS.items()])

        journees = (co[["id_jour", "id_indiv", "no_jour"]].drop_duplicates("id_jour")
                    .reset_index(drop=True))
        ind = ind.merge(journees.groupby("id_indiv").size().rename("n_jours").reset_index(),
                        how="left")

        # --- apports fournis par l'Anses (pour valider notre recalcul) --------
        ap = rename_existing(raw_apports, cols["apports"], "apports", self.log)
        ap = rename_existing(ap, cols["apports_nutrients"], "apports", self.log)
        apn = [n for n in cols["apports_nutrients"].values() if n in ap.columns]
        ap = ap[["id_indiv"] + apn].copy()
        for n in apn:
            ap[n] = to_number(ap[n])
        ap = ap[ap["id_indiv"].isin(ind["id_indiv"])]

        return {
            "individus": ind.reset_index(drop=True),
            "journees": journees,
            "consommations": co[["id_conso", "id_jour", "id_indiv", "code_aliment", "quantite_g",
                                 "doublon_exact"]],
            "aliments": al.reset_index(drop=True),
            "nutriments": nutriments,
            "composition": compo,
            "apports_fournis": ap.reset_index(drop=True),
        }


# --------------------------------------------------------------------------
# INCA 2 (bonus)
# --------------------------------------------------------------------------
class Inca2Loader:
    survey = "INCA2"

    def __init__(self, raw_dir: Path | None = None):
        self.raw_dir = Path(raw_dir) if raw_dir else C.raw_dir("inca2")
        self.log: list[dict] = []
        self.sources: list[dict] = []

    def load(self) -> pd.DataFrame:
        """Renvoie une table individu x apports (format canonique)."""
        frames = {}
        for key in ("indiv", "apports"):
            path = self.raw_dir / C.INCA2_FILES[key]
            frames[key] = read_csv_robust(path)
            self.sources.append({"enquete": self.survey, "table": key, "fichier": path.name,
                                 "sha256": file_sha256(path), "n_lignes": len(frames[key])})
        ind = rename_existing(frames["indiv"], C.INCA2_COLS["indiv"], "indiv", self.log)
        ap = rename_existing(frames["apports"], C.INCA2_COLS["apports"], "apports", self.log)
        ap = rename_existing(ap, C.INCA2_COLS["apports_nutrients"], "apports", self.log)
        ind = ind[[c for c in C.INCA2_COLS["indiv"].values() if c in ind.columns]].copy()
        ind["sexe"] = ind["sexe"].map(C.SEX_CODES)
        nut = [n for n in C.INCA2_COLS["apports_nutrients"].values() if n in ap.columns]
        df = ind.merge(ap[["id_indiv"] + nut], on="id_indiv", how="inner")
        for c in ["age", "poids_enquete"] + nut:
            df[c] = to_number(df[c])
        df = df[df["age"].between(C.AGE_MIN, C.AGE_MAX)].copy()
        df["classe_age"] = age_class(df["age"])
        df["enquete"] = self.survey
        return df.reset_index(drop=True)


# --------------------------------------------------------------------------
# Ciqual
# --------------------------------------------------------------------------
class CiqualLoader:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else C.raw_dir("ciqual") / C.CIQUAL_FILE
        self.log: list[dict] = []

    def load(self) -> pd.DataFrame:
        raw = read_csv_robust(self.path)
        n_text = 0
        df = rename_existing(raw, C.CIQUAL_COLS, "ciqual", self.log)
        df = df[[c for c in C.CIQUAL_COLS.values() if c in df.columns]].copy()
        for n in C.NUTRIENTS:
            if n in df.columns:
                if not pd.api.types.is_numeric_dtype(df[n]):
                    n_text += df[n].astype(str).str.contains(r"[a-z<\-]", regex=True).sum()
                df[n] = to_number(df[n])
        self.log.append({"etape": "nettoyage", "table": "ciqual",
                         "detail": f"{n_text} valeurs texte converties ('traces', '< x', '-')"})
        df["version"] = C.CIQUAL_VERSION
        self.sha256 = file_sha256(self.path)
        return df
