"""
Génère un jeu de données SYNTHÉTIQUE qui imite la structure des fichiers INCA 3,
INCA 2 et Ciqual (mêmes noms de fichiers, mêmes noms de colonnes que config.py,
séparateur ';', décimale ',', encodage latin-1).

But : pouvoir développer, tester et faire tourner tout le pipeline AVANT d'avoir
les vraies données, et disposer d'un jeu de test reproductible (graine fixe).
Les résultats obtenus sur ces données n'ont AUCUNE valeur scientifique.

Quelques défauts de qualité sont injectés volontairement (valeurs manquantes,
doublon, quantité négative, aliment inconnu, valeurs "traces" dans Ciqual...)
pour que le rapport qualité ait quelque chose à détecter.

Usage :  python scripts/make_synthetic_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "synthetic"

# libellé, groupe, prot, gluc, lip, fibres, alcool, Ca, Fe, VitC (pour 100 g), portion (g)
FOODS = [
    ("Pain baguette", "Pain et panification", 8.6, 56.0, 1.3, 2.8, 0, 22, 1.1, 0, 60),
    ("Pain complet", "Pain et panification", 9.0, 45.0, 2.0, 7.0, 0, 30, 2.2, 0, 50),
    ("Céréales petit-déjeuner", "Céréales petit-déjeuner", 7.5, 78.0, 3.0, 4.0, 0, 50, 8.0, 0, 40),
    ("Pâtes cuites", "Pâtes, riz, céréales", 5.0, 30.0, 0.9, 1.8, 0, 9, 0.5, 0, 200),
    ("Riz cuit", "Pâtes, riz, céréales", 2.7, 28.0, 0.3, 0.4, 0, 3, 0.2, 0, 180),
    ("Pomme de terre cuite", "Pommes de terre", 2.0, 17.0, 0.1, 2.0, 0, 6, 0.4, 9, 200),
    ("Frites", "Pommes de terre", 3.4, 36.0, 14.0, 3.0, 0, 12, 0.8, 5, 130),
    ("Lait demi-écrémé", "Lait", 3.3, 4.8, 1.6, 0, 0, 120, 0.0, 1, 200),
    ("Yaourt nature", "Ultra-frais laitier", 4.0, 5.0, 1.5, 0, 0, 140, 0.1, 1, 125),
    ("Fromage blanc", "Ultra-frais laitier", 7.0, 4.0, 3.0, 0, 0, 110, 0.1, 0, 100),
    ("Emmental", "Fromages", 28.0, 0.5, 29.0, 0, 0, 1000, 0.3, 0, 30),
    ("Camembert", "Fromages", 20.0, 0.5, 22.0, 0, 0, 380, 0.2, 0, 30),
    ("Steak haché 15%", "Viande", 19.0, 0.0, 15.0, 0, 0, 10, 2.3, 0, 100),
    ("Poulet rôti", "Volaille", 27.0, 0.0, 6.0, 0, 0, 12, 0.9, 0, 120),
    ("Jambon cuit", "Charcuterie", 20.0, 1.0, 4.0, 0, 0, 8, 0.8, 0, 50),
    ("Saucisson sec", "Charcuterie", 26.0, 2.0, 33.0, 0, 0, 20, 1.5, 0, 30),
    ("Saumon cuit", "Poissons", 24.0, 0.0, 12.0, 0, 0, 12, 0.4, 0, 120),
    ("Thon en conserve", "Poissons", 25.0, 0.0, 1.0, 0, 0, 15, 1.3, 0, 80),
    ("Oeuf dur", "Oeufs", 12.5, 0.7, 10.0, 0, 0, 50, 1.8, 0, 60),
    ("Lentilles cuites", "Légumineuses", 9.0, 17.0, 0.5, 8.0, 0, 20, 3.3, 1, 150),
    ("Carottes cuites", "Légumes", 0.8, 6.0, 0.2, 2.8, 0, 30, 0.3, 4, 120),
    ("Haricots verts cuits", "Légumes", 1.9, 3.5, 0.2, 3.2, 0, 40, 0.8, 10, 120),
    ("Tomate crue", "Légumes", 0.9, 2.8, 0.2, 1.2, 0, 10, 0.3, 14, 100),
    ("Salade verte", "Légumes", 1.3, 1.5, 0.2, 1.3, 0, 30, 0.9, 9, 50),
    ("Brocoli cuit", "Légumes", 2.4, 3.0, 0.4, 3.3, 0, 40, 0.7, 65, 120),
    ("Soupe de légumes", "Soupes", 0.8, 4.0, 0.8, 1.0, 0, 15, 0.3, 3, 250),
    ("Pomme", "Fruits", 0.3, 11.6, 0.2, 1.4, 0, 5, 0.1, 5, 150),
    ("Banane", "Fruits", 1.1, 20.0, 0.3, 2.0, 0, 6, 0.3, 9, 120),
    ("Orange", "Fruits", 0.9, 8.0, 0.2, 2.0, 0, 35, 0.1, 50, 150),
    ("Kiwi", "Fruits", 1.0, 10.0, 0.5, 3.0, 0, 30, 0.3, 80, 80),
    ("Compote", "Compotes et fruits cuits", 0.3, 18.0, 0.1, 1.5, 0, 4, 0.2, 2, 100),
    ("Jus d'orange", "Jus de fruits", 0.7, 9.0, 0.1, 0.2, 0, 10, 0.1, 35, 200),
    ("Beurre", "Matières grasses", 0.7, 0.6, 82.0, 0, 0, 15, 0.0, 0, 10),
    ("Huile d'olive", "Matières grasses", 0.0, 0.0, 100.0, 0, 0, 0, 0.1, 0, 10),
    ("Chocolat noir", "Sucres et confiseries", 7.0, 45.0, 33.0, 11.0, 0, 70, 11.0, 0, 20),
    ("Confiture", "Sucres et confiseries", 0.4, 60.0, 0.1, 1.0, 0, 15, 0.3, 5, 20),
    ("Gâteau au chocolat", "Pâtisseries et gâteaux", 5.5, 50.0, 22.0, 2.0, 0, 50, 2.0, 0, 80),
    ("Viennoiserie croissant", "Viennoiseries", 8.0, 45.0, 21.0, 2.0, 0, 40, 1.0, 0, 50),
    ("Biscuit sec", "Biscuits", 7.0, 72.0, 15.0, 2.5, 0, 50, 2.0, 0, 30),
    ("Pizza", "Plats composés", 10.0, 28.0, 9.0, 2.0, 0, 150, 1.0, 3, 250),
    ("Quiche lorraine", "Plats composés", 10.0, 18.0, 17.0, 1.0, 0, 120, 1.0, 0, 150),
    ("Sandwich jambon beurre", "Sandwichs", 12.0, 38.0, 10.0, 2.0, 0, 40, 1.2, 0, 200),
    ("Soda sucré", "Boissons rafraîchissantes", 0.0, 10.5, 0.0, 0, 0, 3, 0.0, 0, 330),
    ("Eau", "Eaux", 0.0, 0.0, 0.0, 0, 0, 8, 0.0, 0, 300),
    ("Café", "Boissons chaudes", 0.1, 0.3, 0.0, 0, 0, 2, 0.0, 0, 150),
    ("Vin rouge", "Boissons alcoolisées", 0.1, 0.2, 0.0, 0, 10.0, 8, 0.6, 0, 150),
    ("Bière", "Boissons alcoolisées", 0.4, 3.5, 0.0, 0, 4.0, 4, 0.0, 0, 250),
    ("Noix", "Fruits à coque", 15.0, 11.0, 64.0, 6.5, 0, 90, 2.9, 1, 20),
]

# Profils latents (pour que le bonus "profils alimentaires" ait du sens)
PROFILES = {
    "classique": {},
    "végétal": {"Légumes": 2.5, "Fruits": 2.5, "Légumineuses": 3, "Viande": 0.3,
                "Charcuterie": 0.3, "Fruits à coque": 3, "Pain et panification": 1.2},
    "sucré-transformé": {"Sucres et confiseries": 3, "Boissons rafraîchissantes": 4,
                          "Biscuits": 3, "Viennoiseries": 3, "Plats composés": 2,
                          "Pommes de terre": 1.5, "Légumes": 0.4, "Fruits": 0.4},
}


def atwater(p, g, l, f, a):
    return 4 * p + 4 * g + 9 * l + 2 * f + 7 * a


def build_foods(rng):
    rows = []
    for i, (lib, grp, p, g, l, f, a, ca, fe, vc, portion) in enumerate(FOODS):
        kcal = atwater(p, g, l, f, a) * rng.normal(1, 0.02)
        rows.append(dict(code=1000 + i, libelle=lib, groupe=grp, prot=p, glucides=g,
                         lipides=l, fibres=f, alcool=a, calcium=ca, fer=fe,
                         vitamine_c=vc, nrj_kcal=round(kcal, 1), portion=portion))
    return pd.DataFrame(rows)


def make_inca3(rng, foods, n=2000):
    sexe = rng.choice([1, 2], n, p=[0.45, 0.55])
    age = rng.integers(18, 80, n)
    poids = np.where(sexe == 1, rng.normal(80, 13, n), rng.normal(66, 13, n)).clip(40, 160)
    taille = np.where(sexe == 1, rng.normal(176, 7, n), rng.normal(163, 6, n))
    w = rng.lognormal(0, 0.5, n)
    w = w / w.sum() * 49_000_000          # ~ population adulte France métropolitaine
    tage = pd.cut(age, [18, 45, 65, 80], right=False, labels=[1, 2, 3]).astype(int)
    indiv = pd.DataFrame({
        "NOIND": np.arange(110001, 110001 + n), "sex_PS": sexe, "age": age,
        "tage_PS": tage, "poids": poids.round(1), "taille": taille.round(1),
        "pond_indiv_adu_pop2": w.round(2),
    })
    profile = rng.choice(list(PROFILES), n, p=[0.55, 0.25, 0.20])
    underreporter = rng.random(n) < 0.15

    lines = []
    for k in range(n):
        mult = PROFILES[profile[k]]
        prob = foods["groupe"].map(lambda g: mult.get(g, 1.0)).to_numpy()
        prob = prob / prob.sum()
        scale = (1.15 if sexe[k] == 1 else 0.9) * (1.05 - 0.004 * (age[k] - 18))
        scale *= 0.6 if underreporter[k] else 1.0
        n_days = 3 if rng.random() > 0.05 else 2
        for d in range(1, n_days + 1):
            n_items = rng.integers(12, 22)
            idx = rng.choice(len(foods), n_items, p=prob)
            for j in idx:
                q = foods.at[j, "portion"] * rng.lognormal(0, 0.35) * scale
                lines.append((indiv.at[k, "NOIND"], d, int(foods.at[j, "code"]), round(q, 1)))
    conso = pd.DataFrame(lines, columns=["NOIND", "nojour", "aliment_code_INCA3", "qte_conso"])
    nut_cols = ["nrj_kcal", "prot", "glucides", "lipides", "fibres", "alcool",
                "calcium", "fer", "vitamine_c"]
    conso = conso.merge(foods.rename(columns={"code": "aliment_code_INCA3"})
                        [["aliment_code_INCA3"] + nut_cols], how="left")

    # apports "officiels" : moyenne des jours, calculée proprement (+ arrondis)
    tmp = conso.copy()
    for c in nut_cols:
        tmp[c] = tmp["qte_conso"] / 100 * tmp[c]
    day = tmp.groupby(["NOIND", "nojour"])[nut_cols].sum()
    apports = day.groupby("NOIND").mean().round(2).reset_index()

    # --- défauts de qualité injectés volontairement -----------------------
    indiv.loc[rng.choice(n, 25, replace=False), "poids"] = np.nan
    indiv.loc[rng.choice(n, 10, replace=False), "taille"] = np.nan
    conso.loc[5, "qte_conso"] = -50.0                     # quantité négative
    conso.loc[17, "qte_conso"] = 4500.0                   # quantité implausible
    conso = pd.concat([conso, conso.iloc[[30]]], ignore_index=True)   # doublon exact
    bad = conso.iloc[[40]].copy()
    bad["aliment_code_INCA3"] = 9999                      # aliment absent de la nomenclature
    conso = pd.concat([conso, bad], ignore_index=True)

    nomenclature = foods.rename(columns={"code": "aliment_code_INCA3",
                                         "libelle": "aliment_libelle_INCA3",
                                         "groupe": "gpe_INCA3"})[
        ["aliment_code_INCA3", "aliment_libelle_INCA3", "gpe_INCA3"]]
    return indiv, conso, apports, nomenclature


def make_inca2(rng, n=1500):
    sexe = rng.choice([1, 2], n, p=[0.45, 0.55])
    age = rng.integers(18, 80, n)
    base = np.where(sexe == 1, 2300, 1750) * (1.05 - 0.004 * (age - 18))
    e = rng.normal(base, 450).clip(600)
    w = rng.lognormal(0, 0.5, n)
    indiv = pd.DataFrame({"nomen": np.arange(1, n + 1), "sexe_ps": sexe, "v2_age": age,
                          "ponderation": (w / w.mean()).round(4)})
    apports = pd.DataFrame({
        "nomen": indiv["nomen"], "aet": e.round(1),
        "prot": (e * rng.normal(0.165, 0.025, n) / 4).round(1),
        "lip": (e * rng.normal(0.37, 0.05, n) / 9).round(1),
        "glu": (e * rng.normal(0.43, 0.06, n) / 4).round(1),
        "fibres": rng.normal(18, 5, n).clip(3).round(1),
        "calcium": rng.normal(900, 250, n).clip(150).round(0),
        "fer": rng.normal(12, 3, n).clip(3).round(1),
        "vitc": rng.lognormal(np.log(95), 0.45, n).round(1),
    })
    return indiv, apports


def make_ciqual(rng, foods):
    """Table Ciqual simulée : libellés différents de la nomenclature INCA
    (pour le bonus 'mapping'), valeurs texte typiques ('traces', '< 0,5', '-')."""
    rename = {"Pain baguette": "Pain, baguette, courante", "Pâtes cuites": "Pâtes sèches, cuites",
              "Lait demi-écrémé": "Lait demi-écrémé, UHT", "Poulet rôti": "Poulet, rôti",
              "Steak haché 15%": "Boeuf, steak haché 15% MG, cuit", "Oeuf dur": "Oeuf, dur",
              "Jus d'orange": "Jus d'orange, pur jus", "Vin rouge": "Vin rouge 12°"}
    rows = []
    for _, f in foods.iterrows():
        rows.append({
            "alim_code": 20000 + int(f["code"]),
            "alim_nom_fr": rename.get(f["libelle"], f["libelle"] + ", cru ou préparé"),
            "alim_grp_nom_fr": f["groupe"],
            "Energie, Règlement UE N° 1169/2011 (kcal/100 g)": f["nrj_kcal"],
            "Protéines, N x facteur de Jones (g/100 g)": f["prot"],
            "Glucides (g/100 g)": f["glucides"], "Lipides (g/100 g)": f["lipides"],
            "Fibres alimentaires (g/100 g)": f["fibres"], "Alcool (g/100 g)": f["alcool"],
            "Calcium (mg/100 g)": f["calcium"], "Fer (mg/100 g)": f["fer"],
            "Vitamine C (mg/100 g)": f["vitamine_c"],
        })
    ciq = pd.DataFrame(rows).astype(object)
    vc = "Vitamine C (mg/100 g)"
    for i in rng.choice(len(ciq), 6, replace=False):
        ciq.at[i, vc] = rng.choice(["traces", "< 0,5", "-"])
    ciq.at[3, "Fibres alimentaires (g/100 g)"] = "< 0,5"
    # format français : virgule décimale
    for c in ciq.columns[3:]:
        ciq[c] = ciq[c].map(lambda v: str(v).replace(".", ",") if isinstance(v, (float, int)) else v)
    return ciq


def write(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep=";", decimal=",", index=False, encoding="latin-1")


def main():
    rng = np.random.default_rng(SEED)
    foods = build_foods(rng)
    indiv, conso, apports, nomen = make_inca3(rng, foods)
    write(indiv, OUT / "inca3" / "description-indiv.csv")
    write(conso, OUT / "inca3" / "conso-compo-alim.csv")
    write(apports, OUT / "inca3" / "apports-nut-alim.csv")
    write(nomen, OUT / "inca3" / "nomenclature.csv")
    i2, a2 = make_inca2(rng)
    write(i2, OUT / "inca2" / "Table_indiv.csv")
    write(a2, OUT / "inca2" / "Table_apports_nut.csv")
    ciq = make_ciqual(rng, foods)
    (OUT / "ciqual").mkdir(parents=True, exist_ok=True)
    ciq.to_csv(OUT / "ciqual" / "ciqual_2020.csv", sep=";", index=False, encoding="utf-8")
    print(f"Données synthétiques écrites dans {OUT}")
    print(f"  INCA3 : {len(indiv)} individus, {len(conso)} lignes de consommation")
    print(f"  INCA2 : {len(i2)} individus ; Ciqual : {len(ciq)} aliments")


if __name__ == "__main__":
    main()
