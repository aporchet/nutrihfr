"""
Tests automatisés (annexe D) + quelques tests unitaires des fonctions statistiques.

Lancer :  pytest -v          (depuis la racine du dépôt)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nutrihfr import config as C  # noqa: E402
from nutrihfr.intake import IntakeCalculator, atwater_energy, goldberg_cutoff  # noqa: E402
from nutrihfr.loader import CiqualLoader, to_number  # noqa: E402
from nutrihfr.pipeline import NutriPipeline  # noqa: E402
from nutrihfr.stats import weighted_mean, weighted_quantile  # noqa: E402


# ---------------------------------------------------------------- fixtures --
@pytest.fixture(scope="session")
def results(tmp_path_factory):
    """Exécute le pipeline une seule fois pour toute la session de tests."""
    db = tmp_path_factory.mktemp("db") / "test.sqlite"
    return NutriPipeline(db_path=db, verbose=False).run(save=False)


@pytest.fixture
def mini_tables():
    """Mini jeu de données construit à la main : résultats connus d'avance."""
    individus = pd.DataFrame({"id_indiv": [1, 2], "sexe": ["Femme", "Homme"], "age": [30, 50],
                              "poids_kg": [60, 80], "poids_enquete": [1.0, 1.0], "n_jours": [1, 1]})
    aliments = pd.DataFrame({"code_aliment": [10, 20], "libelle": ["Lait", "Pain"],
                             "groupe": ["Lait", "Pain"]})
    composition = pd.DataFrame({
        "code_aliment": [10, 10, 20, 20], "code_nutriment": ["energie_kcal", "calcium_mg"] * 2,
        "valeur_100g": [46.0, 120.0, 277.0, 22.0]})
    consommations = pd.DataFrame({"id_conso": [1, 2, 3], "id_jour": ["1_1", "1_1", "2_1"],
                                  "id_indiv": [1, 1, 2], "code_aliment": [10, 20, 10],
                                  "quantite_g": [200.0, 100.0, 0.0]})
    return {"individus": individus, "aliments": aliments,
            "composition": composition, "consommations": consommations}


# ------------------------------------------------------------ annexe D ------
def test_1_aucune_quantite_negative(results):
    assert (results["tables"]["consommations"]["quantite_g"] >= 0).all()


def test_2_tous_les_nutriments_ont_une_unite_connue(results):
    nut = results["tables"]["nutriments"]
    assert nut["unite"].isin(["kcal", "g", "mg", "µg"]).all()
    assert set(results["nutrients"]) <= set(C.NUTRIENTS)


def test_3_tout_aliment_consomme_a_une_composition_ou_est_une_exception(results):
    t = results["tables"]
    consumed = set(t["consommations"]["code_aliment"])
    with_compo = set(t["composition"]["code_aliment"])
    exceptions = set(t["exclusions"].loc[
        t["exclusions"]["motif"].str.contains("nomenclature"), "code_aliment"])
    assert consumed <= with_compo
    assert all(code not in consumed for code in exceptions)


def test_4_calcul_pour_un_aliment_connu(mini_tables):
    lines = IntakeCalculator(mini_tables).line_intakes()
    lait = lines[(lines["id_conso"] == 1)].iloc[0]
    assert lait["calcium_mg"] == pytest.approx(200 / 100 * 120)   # 240 mg
    assert lait["energie_kcal"] == pytest.approx(92.0)


def test_5_zero_gramme_donne_zero_apport(mini_tables):
    ind = IntakeCalculator(mini_tables).individual_intakes()
    row = ind[ind["id_indiv"] == 2].iloc[0]
    assert row["energie_kcal"] == 0 and row["calcium_mg"] == 0


def test_6_somme_des_poids_coherente(results):
    w = results["indiv"]["poids_enquete"]
    s, n = w.sum(), len(w)
    normalised = abs(s - n) / n < C.REF_POP_TOLERANCE          # poids ramenés à l'effectif
    extrapolated = abs(s - C.REF_POP_ADULTES) / C.REF_POP_ADULTES < C.REF_POP_TOLERANCE
    assert normalised or extrapolated, f"somme des poids = {s:,.0f}"


def test_7_energie_atwater_proche_de_ciqual():
    ciq = CiqualLoader().load().set_index("code_ciqual")
    e_calc = atwater_energy(ciq)
    ok = ciq["energie_kcal"] > 20                 # écarts relatifs instables si ~0 kcal
    rel = (e_calc[ok] - ciq.loc[ok, "energie_kcal"]).abs() / ciq.loc[ok, "energie_kcal"]
    assert (rel < 0.10).mean() >= 0.95, rel.sort_values().tail()


# ------------------------------------------------- tests complémentaires -----
def test_apports_recalcules_proches_de_ceux_fournis(results):
    v = results["validation"].set_index("nutriment")
    assert v.loc["energie_kcal", "correlation"] > 0.99


def test_conversion_valeurs_ciqual():
    s = pd.Series(["traces", "< 0,5", "-", "12,3", None])
    out = to_number(s)
    assert out.iloc[0] == 0 and out.iloc[1] == 0.25 and np.isnan(out.iloc[2])
    assert out.iloc[3] == pytest.approx(12.3)


def test_moyenne_et_mediane_ponderees():
    assert weighted_mean([1, 2, 3], [1, 1, 2]) == pytest.approx(2.25)
    assert weighted_quantile([1, 2, 3, 4], [1, 1, 1, 1], 0.5) == pytest.approx(2.5)


def test_seuil_goldberg_plausible():
    assert 0.9 < goldberg_cutoff(3) < 1.1        # ~1.0 pour 3 jours, PAL 1.55


def test_integrite_referentielle_sqlite(results, tmp_path):
    from nutrihfr.database import NutriDatabase
    db = NutriDatabase(tmp_path / "x.sqlite")
    t = dict(results["tables"])
    db.load(t)
    assert db.check_integrity().empty
