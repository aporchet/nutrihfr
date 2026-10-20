"""Relance tout le pipeline depuis les fichiers bruts : python scripts/run_pipeline.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nutrihfr import config as C
from nutrihfr.pipeline import CalculApports, ChargeurINCA3, ControleQualite, creer_base_sqlite

individus, consommations, apports_anses = ChargeurINCA3().charger()
print(f"{len(individus)} adultes, {len(consommations)} lignes de consommation")

qualite = ControleQualite(individus, consommations).executer()
print(qualite.to_string(index=False))

calcul = CalculApports(consommations, individus)
apports = calcul.par_individu()

C.DOSSIER_TRAITE.mkdir(parents=True, exist_ok=True)
C.DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
apports.to_csv(C.DOSSIER_TRAITE / "apports_individuels.csv", index=False)
qualite.to_csv(C.DOSSIER_TABLES / "rapport_qualite.csv", index=False)
print(creer_base_sqlite(individus, consommations, apports))
print("Pipeline terminé.")
