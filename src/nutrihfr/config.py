"""
Configuration centrale du projet NutriHFr.

C'est le SEUL fichier à modifier pour passer des données synthétiques aux vraies
données INCA. Toutes les correspondances "nom de colonne brut -> nom canonique"
sont ici, pour que le reste du code ne dépende jamais des noms bruts.

Les noms marqués  # A VERIFIER  sont ceux supposés pour les fichiers INCA 3 de
data.gouv.fr : lance le notebook 01 (cellule "inspection des colonnes") et
corrige-les si besoin.
"""
import os
from pathlib import Path

# --------------------------------------------------------------------------
# Chemins
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"
DB_PATH = DATA_PROCESSED / "nutrihfr.sqlite"
SCHEMA_SQL = ROOT / "sql" / "schema.sql"

# "synthetic" : données simulées (data/raw/synthetic), pour développer et tester
# "real"      : vrais fichiers INCA déposés dans data/raw/inca3 (et inca2)
# (la variable d'environnement NUTRIHFR_MODE est prioritaire : utilisée par la CI GitHub)
MODE = os.environ.get("NUTRIHFR_MODE", "synthetic")

# --------------------------------------------------------------------------
# Nutriments étudiés (noms canoniques utilisés partout dans le projet)
# --------------------------------------------------------------------------
NUTRIENTS = {
    # code canonique : (libellé, unité)
    "energie_kcal": ("Énergie", "kcal"),
    "proteines_g": ("Protéines", "g"),
    "glucides_g": ("Glucides", "g"),
    "lipides_g": ("Lipides", "g"),
    "fibres_g": ("Fibres alimentaires", "g"),
    "alcool_g": ("Alcool", "g"),
    "calcium_mg": ("Calcium", "mg"),
    "fer_mg": ("Fer", "mg"),
    "vitc_mg": ("Vitamine C", "mg"),
}
CONTRIB_NUTRIENTS = ["proteines_g", "calcium_mg", "fer_mg", "fibres_g", "vitc_mg"]  # Q5

# Coefficients d'Atwater (kcal/g) - règlement UE 1169/2011 (fibres = 2 kcal/g)
ATWATER = {"proteines_g": 4, "glucides_g": 4, "lipides_g": 9, "fibres_g": 2, "alcool_g": 7}

# --------------------------------------------------------------------------
# Population d'étude
# --------------------------------------------------------------------------
AGE_MIN, AGE_MAX = 18, 79                      # adultes uniquement (choix du projet)
AGE_BINS = [18, 25, 45, 65, 80]                # bornes [a, b[
AGE_LABELS = ["18-24", "25-44", "45-64", "65-79"]
# Population de référence pour le test 6 (somme des pondérations).
# Ordre de grandeur : adultes 18-79 ans en France métropolitaine vers 2015 (INSEE,
# estimations de population) ~ 47 millions. A AFFINER avec la source INSEE citée.
REF_POP_ADULTES = 47_000_000
REF_POP_TOLERANCE = 0.10

# --------------------------------------------------------------------------
# Sous-déclaration (critère de Goldberg, version Black 2000)
# --------------------------------------------------------------------------
GOLDBERG = {
    "pal": 1.55,      # niveau d'activité physique supposé (sédentaire-modéré)
    "cv_wei": 23.0,   # CV intra-individuel de l'apport énergétique (%)
    "cv_wb": 8.5,     # CV du métabolisme de base estimé (%)
    "cv_tp": 15.0,    # CV de la dépense totale (%)
    "sd_min": -2.0,   # IC 95 % unilatéral
}

# --------------------------------------------------------------------------
# INCA 3 : fichiers et colonnes
# --------------------------------------------------------------------------
INCA3_FILES = {
    "indiv": "description-indiv.csv",
    "conso": "conso-compo-alim.csv",
    "apports": "apports-nut-alim.csv",
    "nomenclature": "nomenclature.csv",
}

INCA3_COLS = {
    "indiv": {
        "NOIND": "id_indiv",                 # A VERIFIER
        "sex_PS": "sexe",                    # A VERIFIER (1 = homme, 2 = femme)
        "age": "age",                        # A VERIFIER (si absent : voir AGE_FROM_CLASS)
        "tage_PS": "classe_age_src",         # A VERIFIER
        "poids": "poids_kg",                 # A VERIFIER
        "taille": "taille_cm",               # A VERIFIER
        "pond_indiv_adu_pop2": "poids_enquete",  # A VERIFIER (pondération adultes)
    },
    "conso": {
        "NOIND": "id_indiv",
        "nojour": "no_jour",                 # A VERIFIER
        "aliment_code_INCA3": "code_aliment",  # A VERIFIER
        "qte_conso": "quantite_g",           # A VERIFIER
    },
    # colonnes nutriments présentes dans conso-compo-alim (composition de l'aliment)
    "conso_nutrients": {
        "nrj_kcal": "energie_kcal",          # A VERIFIER
        "prot": "proteines_g",               # A VERIFIER
        "glucides": "glucides_g",            # A VERIFIER
        "lipides": "lipides_g",              # A VERIFIER
        "fibres": "fibres_g",                # A VERIFIER
        "alcool": "alcool_g",                # A VERIFIER
        "calcium": "calcium_mg",             # A VERIFIER
        "fer": "fer_mg",                     # A VERIFIER
        "vitamine_c": "vitc_mg",             # A VERIFIER
    },
    "nomenclature": {
        "aliment_code_INCA3": "code_aliment",   # A VERIFIER
        "aliment_libelle_INCA3": "libelle",     # A VERIFIER
        "gpe_INCA3": "groupe",                  # A VERIFIER (code ou libellé de groupe)
    },
    # apports journaliers moyens fournis par l'Anses (validation du pipeline)
    "apports": {"NOIND": "id_indiv"},
    "apports_nutrients": {
        "nrj_kcal": "energie_kcal",          # A VERIFIER
        "prot": "proteines_g",
        "glucides": "glucides_g",
        "lipides": "lipides_g",
        "fibres": "fibres_g",
        "alcool": "alcool_g",
        "calcium": "calcium_mg",
        "fer": "fer_mg",
        "vitamine_c": "vitc_mg",
    },
}

# Codage du sexe dans le fichier brut
SEX_CODES = {1: "Homme", 2: "Femme"}

# Les valeurs nutritionnelles de conso-compo-alim sont-elles exprimées
# "pour 100 g" d'aliment, ou "pour la quantité consommée" ? (voir notebook 02)
COMPO_EMBARQUEE_PAR = "100g"   # "100g" ou "portion"

# Si l'âge exact n'est pas diffusé, âge approximé par le milieu de classe
AGE_FROM_CLASS = {}  # ex. {1: 21, 2: 35, 3: 55, 4: 72} une fois les codes connus

# --------------------------------------------------------------------------
# INCA 2 (bonus : comparaison d'enquêtes)
# --------------------------------------------------------------------------
INCA2_FILES = {
    "indiv": "Table_indiv.csv",            # A VERIFIER
    "apports": "Table_apports_nut.csv",    # A VERIFIER (apports journaliers, 38 nutriments)
}
INCA2_COLS = {
    "indiv": {
        "nomen": "id_indiv",               # A VERIFIER
        "sexe_ps": "sexe",                 # A VERIFIER
        "v2_age": "age",                   # A VERIFIER
        "ponderation": "poids_enquete",    # A VERIFIER
    },
    "apports": {"nomen": "id_indiv"},
    "apports_nutrients": {
        "aet": "energie_kcal",             # A VERIFIER (apport énergétique total)
        "prot": "proteines_g",
        "lip": "lipides_g",
        "glu": "glucides_g",
        "fibres": "fibres_g",
        "calcium": "calcium_mg",
        "fer": "fer_mg",
        "vitc": "vitc_mg",
    },
}

# --------------------------------------------------------------------------
# Ciqual (source externe de composition)
# --------------------------------------------------------------------------
CIQUAL_FILE = "ciqual_2020.csv"    # export de https://ciqual.anses.fr (xls -> csv)
CIQUAL_VERSION = "Ciqual 2020"
CIQUAL_COLS = {
    "alim_code": "code_ciqual",
    "alim_nom_fr": "libelle",
    "alim_grp_nom_fr": "groupe",
    "Energie, Règlement UE N° 1169/2011 (kcal/100 g)": "energie_kcal",
    "Protéines, N x facteur de Jones (g/100 g)": "proteines_g",
    "Glucides (g/100 g)": "glucides_g",
    "Lipides (g/100 g)": "lipides_g",
    "Fibres alimentaires (g/100 g)": "fibres_g",
    "Alcool (g/100 g)": "alcool_g",
    "Calcium (mg/100 g)": "calcium_mg",
    "Fer (mg/100 g)": "fer_mg",
    "Vitamine C (mg/100 g)": "vitc_mg",
}


def raw_dir(survey: str = "inca3") -> Path:
    """Dossier des fichiers bruts selon le mode choisi."""
    if MODE == "synthetic":
        return DATA_RAW / "synthetic" / survey
    return DATA_RAW / survey
