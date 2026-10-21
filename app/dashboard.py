"""Dashboard NutriHFr : exploration interactive des apports nutritionnels (INCA 3).

Lancer depuis la racine du projet :
    streamlit run app/dashboard.py

Seuls des résultats agrégés et pondérés sont affichés (aucune donnée individuelle).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nutrihfr import config as C
from nutrihfr.pipeline import CalculApports, ChargeurINCA3
from nutrihfr.stats import contributions, resume_pondere

st.set_page_config(page_title="NutriHFr", layout="wide")


@st.cache_data
def charger_donnees():
    """Exécute le pipeline une seule fois (mis en cache) : apports par individu et par ligne."""
    individus, consommations, _ = ChargeurINCA3().charger()
    calcul = CalculApports(consommations, individus)
    return calcul.par_individu(), calcul.par_ligne()


apports, lignes = charger_donnees()

# --- Filtres (barre latérale) ---------------------------------------------------
st.sidebar.header("Filtres")
nutriment = st.sidebar.selectbox("Nutriment", list(C.NUTRIMENTS),
                                 format_func=lambda n: f"{C.NUTRIMENTS[n][0]} ({C.NUTRIMENTS[n][1]})")
sexes = st.sidebar.multiselect("Sexe", ["Femme", "Homme"], default=["Femme", "Homme"])
ages = st.sidebar.multiselect("Classe d'âge", list(C.CLASSES_AGE.values()),
                              default=list(C.CLASSES_AGE.values()))
densite = st.sidebar.checkbox("Exprimer pour 1 000 kcal", value=False, disabled=(nutriment == "aet"))

selection = apports[apports["sexe"].isin(sexes) & apports["classe_age"].isin(ages)].copy()
unite = f"{C.NUTRIMENTS[nutriment][1]}/j"
variable = nutriment
if densite and nutriment != "aet":
    variable = nutriment + "_1000kcal"
    selection[variable] = selection[nutriment] / selection["aet"] * 1000
    unite = f"{C.NUTRIMENTS[nutriment][1]}/1000 kcal"

# --- En-tête et chiffres clés ---------------------------------------------------
st.title("NutriHFr : apports nutritionnels des adultes en France")
st.caption("Source : INCA 3 (Anses, 2014-2015), adultes de 18-79 ans. "
           "Estimations pondérées (pond_indiv_adu_pop3), IC 95 %.")

if len(selection) < 30:
    st.warning("Sélection trop petite (moins de 30 personnes) : choisissez d'autres filtres.")
    st.stop()

r = resume_pondere(selection, variable).iloc[0]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Adultes", f"{int(r['n'])}")
col2.metric(f"Moyenne ({unite})", f"{r['moyenne']:,.1f}".replace(",", " "))
col3.metric("IC 95 %", f"{r['ic95_bas']:,.1f} – {r['ic95_haut']:,.1f}".replace(",", " "))
col4.metric("Médiane", f"{r['mediane']:,.1f}".replace(",", " "))

# --- Graphiques -----------------------------------------------------------------
gauche, droite = st.columns(2)

with gauche:
    st.subheader("Distribution")
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for sexe in sexes:
        d = selection[selection["sexe"] == sexe]
        ax.hist(d[variable], bins=40, weights=d["ponderation"], density=True, alpha=0.5,
                color=C.COULEURS_SEXE[sexe], label=sexe)
    ax.set(xlabel=unite, ylabel="densité")
    ax.legend()
    st.pyplot(fig)

with droite:
    st.subheader("Moyenne par classe d'âge")
    par_age = resume_pondere(selection, variable, par=["sexe", "classe_age"])
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for sexe in sexes:
        d = par_age[par_age["sexe"] == sexe]
        ax.errorbar(d["classe_age"], d["moyenne"],
                    yerr=[d["moyenne"] - d["ic95_bas"], d["ic95_haut"] - d["moyenne"]],
                    marker="o", capsize=3, color=C.COULEURS_SEXE[sexe], label=sexe)
    ax.set(ylabel=unite)
    ax.legend()
    st.pyplot(fig)

st.subheader("Principaux groupes d'aliments contributeurs")
lignes_sel = lignes[lignes["NOIND"].isin(selection["NOIND"])]
contrib = contributions(lignes_sel, selection, nutriment).head(10).sort_values()
fig, ax = plt.subplots(figsize=(9, 4))
ax.barh(contrib.index, contrib.values, color=C.PALETTE[0])
for y, v in enumerate(contrib.values):
    ax.text(v + 0.3, y, f"{v:.1f} %", va="center", fontsize=8)
ax.set(xlabel="% de l'apport total de la population (ratio des moyennes, pondéré)")
st.pyplot(fig)

with st.expander("Tableau détaillé"):
    st.dataframe(par_age.round(1), use_container_width=True)
