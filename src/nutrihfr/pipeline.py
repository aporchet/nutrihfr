"""
Pipeline NutriHFr de bout en bout :

    chargement -> contrôle qualité -> nettoyage -> calcul des apports
    -> sous-déclaration -> base SQLite -> fichiers de sortie + journal d'exécution

Relançable : `python scripts/run_pipeline.py` reconstruit tout depuis data/raw.
"""
from __future__ import annotations

import json
import platform
from datetime import datetime

import numpy as np
import pandas as pd

from . import config as C
from .database import NutriDatabase
from .intake import IntakeCalculator, add_density, flag_underreporters
from .lineage import git_commit
from .loader import Inca3Loader
from .quality import DataCleaner, QualityChecker


class NutriPipeline:
    def __init__(self, raw_dir=None, db_path=C.DB_PATH, verbose=True):
        self.loader = Inca3Loader(raw_dir)
        self.db = NutriDatabase(db_path)
        self.verbose = verbose
        self.results: dict[str, pd.DataFrame] = {}

    def _say(self, msg):
        if self.verbose:
            print(f"[pipeline] {msg}")

    def run(self, save: bool = True) -> dict[str, pd.DataFrame]:
        self._say(f"mode = {C.MODE} ; dossier = {self.loader.raw_dir}")
        tables = self.loader.load()
        self._say(f"chargé : {len(tables['individus'])} individus, "
                  f"{len(tables['consommations'])} lignes de consommation")

        quality = QualityChecker(tables).run(self.loader.sources)
        self._say(f"contrôle qualité : {(quality['statut'] != 'OK').sum()} points d'attention")

        cleaner = DataCleaner(tables)
        clean = cleaner.run()
        clean["composition"] = clean["composition"][
            clean["composition"]["code_aliment"].isin(clean["aliments"]["code_aliment"])]
        self._say(f"nettoyage : {len(clean['exclusions'])} lignes écartées")

        calc = IntakeCalculator(clean)
        lines = calc.line_intakes()
        daily = calc.daily_intakes(lines)
        indiv = calc.individual_intakes(daily)
        indiv = flag_underreporters(indiv)
        indiv = add_density(indiv, calc.nutrients)
        self._say(f"apports calculés pour {len(indiv)} individus ; "
                  f"{indiv['sous_declarant'].eq(True).mean():.1%} de sous-déclarants (Goldberg)")

        validation = self.validate(indiv, clean["apports_fournis"], calc.nutrients)

        long = indiv.melt(id_vars="id_indiv", value_vars=calc.nutrients,
                          var_name="code_nutriment", value_name="valeur")
        db_tables = dict(clean)
        db_tables["apports_individuels"] = long
        db_tables["sources"] = pd.DataFrame(self.loader.sources).rename(
            columns={"table": "table_src"})
        self.db.load(db_tables)
        fk = self.db.check_integrity()
        self._say(f"base SQLite écrite ({self.db.path.name}) ; violations de clés : {len(fk)}")

        self.results = {"tables": clean, "quality": quality, "exclusions_summary": cleaner.summary(),
                        "lines": lines, "daily": daily, "indiv": indiv,
                        "validation": validation, "nutrients": calc.nutrients,
                        "load_log": pd.DataFrame(self.loader.log)}
        if save:
            self.save()
        return self.results

    @staticmethod
    def validate(indiv, provided, nutrients) -> pd.DataFrame:
        """Compare nos apports recalculés aux apports fournis par l'Anses."""
        m = indiv[["id_indiv"] + nutrients].merge(provided, on="id_indiv",
                                                  suffixes=("_calc", "_anses"))
        rows = []
        for n in nutrients:
            if f"{n}_anses" not in m:
                continue
            a, b = m[f"{n}_calc"], m[f"{n}_anses"]
            rel = (a - b).abs() / b.replace(0, np.nan)
            rows.append({"nutriment": n, "n": int(a.notna().sum()),
                         "correlation": a.corr(b),
                         "ecart_relatif_median_pct": 100 * rel.median(),
                         "pct_individus_ecart_<5%": 100 * (rel < 0.05).mean()})
        return pd.DataFrame(rows)

    def save(self):
        C.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        C.TABLES.mkdir(parents=True, exist_ok=True)
        r = self.results
        r["indiv"].to_csv(C.DATA_PROCESSED / "apports_individuels.csv", index=False)
        r["daily"].to_csv(C.DATA_PROCESSED / "apports_journaliers.csv", index=False)
        r["lines"].to_csv(C.DATA_PROCESSED / "consommations_nutriments.csv", index=False)
        r["quality"].to_csv(C.TABLES / "data_quality_report.csv", index=False)
        r["validation"].to_csv(C.TABLES / "validation_vs_anses.csv", index=False)
        md = QualityChecker.to_markdown(r["quality"])
        md += "\n## Lignes écartées au nettoyage\n\n| Motif | Lignes |\n|---|---|\n"
        md += "".join(f"| {m} | {n} |\n" for m, n in r["exclusions_summary"].itertuples(index=False))
        md += "\n## Validation : apports recalculés vs apports fournis par l'Anses\n\n"
        md += "| Nutriment | n | Corrélation | Écart relatif médian (%) | % individus écart < 5 % |\n"
        md += "|---|---|---|---|---|\n"
        for v in r["validation"].itertuples(index=False):
            md += f"| {v[0]} | {v[1]} | {v[2]:.4f} | {v[3]:.2f} | {v[4]:.1f} |\n"
        (C.ROOT / "docs" / "data_quality_report.md").write_text(md, encoding="utf-8")
        run_log = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "mode": C.MODE, "git_commit": git_commit(),
            "python": platform.python_version(), "pandas": pd.__version__,
            "sources": self.loader.sources, "journal_chargement": self.loader.log,
            "n_individus": int(len(r["indiv"])),
            "n_exclusions": int(len(r["tables"]["exclusions"])),
        }
        (C.DATA_PROCESSED / "run_log.json").write_text(
            json.dumps(run_log, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


