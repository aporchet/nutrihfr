"""Paramètres du projet NutriHFr : chemins, fichiers INCA 3 et variables utilisées.

Toutes les correspondances (codes, numéros de nutriments, classes d'âge) viennent
de la notice utilisateurs INCA 3 (Anses, janvier 2021).
"""
from pathlib import Path

# --- Chemins ------------------------------------------------------------------
RACINE = Path(__file__).resolve().parents[2]
DOSSIER_BRUT = RACINE / "data" / "raw" / "inca3"
DOSSIER_TRAITE = RACINE / "data" / "processed"
DOSSIER_FIGURES = RACINE / "outputs" / "figures"
DOSSIER_TABLES = RACINE / "outputs" / "tables"
BASE_SQLITE = DOSSIER_TRAITE / "nutrihfr.sqlite"
SCHEMA_SQL = RACINE / "sql" / "schema.sql"

# --- Fichiers INCA 3 (noms tels que téléchargés sur data.gouv.fr) --------------
FICHIERS = {
    "individus": "description-indiv.csv",
    "consommations": "conso-compo-alim-vf-mad-datagouv2021.csv",
    "apports": "apports-nut-alim.csv",
}

# --- Population étudiée : adultes participants au volet consommation (Pop3) ----
PONDERATION = "pond_indiv_adu_pop3"          # pondération des adultes "participants CONSO"
SEXES = {1: "Homme", 2: "Femme"}              # format_sex
CLASSES_AGE = {7: "18-44 ans", 8: "45-64 ans", 9: "65-79 ans"}   # format_tage_PS
AGE_MILIEU = {7: 31, 8: 55, 9: 72}           # âge approché (milieu de classe), pour Goldberg

# --- Nutriments étudiés --------------------------------------------------------
# nom de colonne dans conso-compo-alim : (libellé, unité, colonne dans apports-nut-alim)
# Dans conso-compo-alim, les valeurs sont données pour 100 g d'aliment.
NUTRIMENTS = {
    "aet":        ("Énergie", "kcal", "nutriment1"),
    "proteines":  ("Protéines", "g", "nutriment3"),
    "glucides":   ("Glucides", "g", "nutriment4"),
    "fibres":     ("Fibres", "g", "nutriment8"),
    "lipides":    ("Lipides", "g", "nutriment10"),
    "alcool":     ("Alcool", "g", "nutriment28"),
    "calcium":    ("Calcium", "mg", "nutriment35"),
    "fer":        ("Fer", "mg", "nutriment37"),
    "vitamine_c": ("Vitamine C", "mg", "nutriment51"),
}
NUTRIMENTS_Q5 = ["proteines", "calcium", "fer", "fibres", "vitamine_c"]

# --- Groupes d'aliments INCA 3 (format_gpe_INCA3) ------------------------------
GROUPES = {
    1: "Pain et panification raffinés", 2: "Pain et panification complets",
    3: "Céréales petit-déjeuner et barres", 4: "Pâtes, riz, céréales raffinés",
    5: "Pâtes, riz, céréales complets", 6: "Viennoiseries, pâtisseries, biscuits sucrés",
    7: "Laits", 8: "Yaourts et fromages blancs", 9: "Fromages",
    10: "Entremets et crèmes desserts", 11: "Glaces et sorbets",
    12: "Matières grasses animales", 13: "Matières grasses végétales",
    14: "Oeufs et plats à base d'oeufs", 15: "Viandes (hors volailles)", 16: "Volailles",
    17: "Charcuterie", 18: "Poissons", 19: "Crustacés et mollusques", 20: "Abats",
    21: "Légumes", 22: "Légumineuses", 23: "Pommes de terre et tubercules",
    24: "Fruits frais et secs", 25: "Compotes et fruits au sirop",
    26: "Noix et graines oléagineuses", 27: "Confiserie et chocolat",
    28: "Sucre et matières sucrantes", 29: "Eaux embouteillées", 30: "Eau du robinet",
    31: "Boissons sans alcool (BRSA)", 32: "Jus de fruits et de légumes",
    33: "Boissons alcoolisées", 34: "Boissons chaudes", 35: "Soupes et bouillons",
    36: "Plats à base de viandes", 37: "Plats à base de poissons",
    38: "Plats à base de légumes", 39: "Plats à base de féculents",
    40: "Sandwichs, pizzas, tartes salées", 41: "Condiments, épices et sauces",
    42: "Substituts végétaux (soja…)", 43: "Plats et desserts infantiles",
    44: "Laits et boissons infantiles",
}

# --- Graphiques ----------------------------------------------------------------
COULEURS_SEXE = {"Homme": "#2a78d6", "Femme": "#eb6834"}
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
