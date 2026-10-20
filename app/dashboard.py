"""
Dashboard NutriHFr (Streamlit).

Lancer depuis la racine du dépôt :
    python scripts/run_pipeline.py      # produit data/processed/*.csv
    streamlit run app/dashboard.py

Affiche uniquement des résultats AGRÉGÉS et pondérés ; les groupes de moins de
30 individus sont masqués (confidentialité + précision insuffisante).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nutrihfr import config as C  # noqa: E402
from nutrihfr.intake import IntakeCalculator  # noqa: E402
from nutrihfr.stats import describe_weighted  # noqa: E402
from nutrihfr.viz import PALETTE, SEX_COLORS, set_style, top_n_with_other  # noqa: E402

MIN_N = 30
set_style()
st.set_page_config(page_title="NutriHFr", layout="wide")


@st.cache_data
def load():
    indiv = pd.read_csv(C.DATA_PROCESSED / "apports_individuels.csv")
    lines = pd.read_csv(C.DATA_PROCESSED / "consommations_nutriments.csv")
    return indiv, lines


if not (C.DATA_PROCESSED / "apports_individuels.csv").exists():
    st.error("Données absentes : lancez d'abord `python scripts/run_pipeline.py`.")
    st.stop()

indiv, lines = load()

# ------------------------------------------------------------------ filtres
st.sidebar.title("Filtres")
nutr = st.sidebar.selectbox("Nutriment", list(C.NUTRIENTS),
                            format_func=lambda n: f"{C.NUTRIENTS[n][0]} ({C.NUTRIENTS[n][1]})")
sexes = st.sidebar.multiselect("Sexe", ["Femme", "Homme"], default=["Femme", "Homme"])
ages = st.sidebar.multiselect("Classe d'âge", C.AGE_LABELS, default=C.AGE_LABELS)
excl = st.sidebar.checkbox("Exclure les sous-déclarants (Goldberg)", value=False)
dens = st.sidebar.checkbox("Exprimer pour 1 000 kcal", value=False) and nutr != "energie_kcal"

d = indiv[indiv["sexe"].isin(sexes) & indiv["classe_age"].isin(ages)]
if excl:
    d = d[d["sous_declarant"].astype(str).str.lower().isin(["false", "0", "0.0"])]
var = f"{nutr}_per1000kcal" if dens else nutr
unit = f"{C.NUTRIENTS[nutr][1]}/1000 kcal" if dens else f"{C.NUTRIENTS[nutr][1]}/j"

st.title("NutriHFr — apports nutritionnels des adultes en France (INCA 3)")
st.caption(f"Mode des données : **{C.MODE}** · estimations pondérées · groupes < {MIN_N} individus masqués")
if C.MODE == "synthetic":
    st.warning("Données SYNTHÉTIQUES : résultats sans valeur scientifique.")

if len(d) < MIN_N:
    st.info("Sélection trop petite pour être affichée.")
    st.stop()

# ------------------------------------------------------------------ chiffres clés
s = describe_weighted(d, var).iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Individus", f"{int(s.n):,}".replace(",", " "))
c2.metric(f"Moyenne ({unit})", f"{s.moyenne:,.1f}", help=f"IC 95 % : {s.ic95_bas:,.1f} – {s.ic95_haut:,.1f}")
c3.metric("Médiane", f"{s.mediane:,.1f}")
c4.metric("P5 – P95", f"{s.P5:,.0f} – {s.P95:,.0f}")

# ------------------------------------------------------------------ graphiques
left, right = st.columns(2)
with left:
    st.subheader("Distribution")
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for sx in sexes:
        ds = d[d["sexe"] == sx]
        ax.hist(ds[var], bins=40, weights=ds["poids_enquete"], density=True, alpha=0.45,
                color=SEX_COLORS[sx], label=sx)
    ax.set(xlabel=unit, ylabel="densité"); ax.legend()
    st.pyplot(fig)

with right:
    st.subheader("Par classe d'âge et sexe")
    t = describe_weighted(d, var, by=["sexe", "classe_age"])
    t = t[t["n"] >= MIN_N]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for sx in sexes:
        ts = t[t["sexe"] == sx].set_index("classe_age").reindex(C.AGE_LABELS).dropna(subset=["moyenne"])
        ax.errorbar(ts.index, ts["moyenne"], yerr=[ts["moyenne"] - ts["ic95_bas"], ts["ic95_haut"] - ts["moyenne"]],
                    marker="o", capsize=3, lw=2, color=SEX_COLORS[sx], label=sx)
    ax.set(ylabel=unit); ax.legend()
    st.pyplot(fig)

st.subheader("Principaux groupes d'aliments contributeurs")
ld = lines[lines["id_indiv"].isin(d["id_indiv"])]
contrib = IntakeCalculator.contributions(ld, d, nutr).set_index("groupe")["contribution_pct"]
top = top_n_with_other(contrib, n=10)[::-1]
fig, ax = plt.subplots(figsize=(9, 4))
ax.barh(top.index, top.values, color=[("#b5b4ad" if g == "Autres" else PALETTE[0]) for g in top.index], height=0.6)
for y, v in enumerate(top.values):
    ax.text(v + 0.3, y, f"{v:.1f} %", va="center", fontsize=8)
ax.set(xlabel="% de l'apport total (ratio des moyennes, pondéré)")
st.pyplot(fig)

with st.expander("Tableau détaillé (pondéré)"):
    st.dataframe(t.round(1), use_container_width=True)
    st.download_button("Télécharger (CSV)", t.to_csv(index=False).encode("utf-8"), "nutrihfr_selection.csv")

with st.expander("Méthode et traçabilité"):
    st.markdown(
        "- Source : INCA 3 (Anses, 2014-2015), adultes 18-79 ans.\n"
        "- Apport individuel = moyenne des jours de recueil ; formule `quantité/100 × teneur pour 100 g`.\n"
        "- Moyennes et percentiles pondérés (`pond_indiv_adu_pop2`), IC 95 % par linéarisation.\n"
        "- Sous-déclarants : critère de Goldberg (Black 2000), PAL = 1,55.\n"
        "- Journal d'exécution : `data/processed/run_log.json`.")
