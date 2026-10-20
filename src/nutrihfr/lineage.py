"""Lignage des résultats (annexe C) : chaque chiffre publié peut être reproduit."""
from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime

from . import config as C


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=C.ROOT,
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "non versionné"


@dataclass
class Lineage:
    resultat: str
    population: dict
    source_consommation: str = "INCA 3 (Anses, 2014-2015) - data.gouv.fr"
    composition: str = "composition embarquée INCA 3 (conso-compo-alim)"
    mapping: str = "code_aliment INCA 3 (identité, pas de mapping externe)"
    formule: str = "quantite_g / 100 x valeur_100g"
    agregation: str = "somme par jour, moyenne des jours par individu, puis moyenne pondérée"
    ponderation: str = "poids_enquete (pond_indiv_adu_pop2)"
    exclusions: str = "voir table SQL 'exclusions'"
    mode_donnees: str = field(default_factory=lambda: C.MODE)
    code: str = field(default_factory=git_commit)
    date: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def tree(self) -> str:
        d = self.to_dict()
        lines = [d.pop("resultat")]
        items = list(d.items())
        for i, (k, v) in enumerate(items):
            last = i == len(items) - 1
            lines.append(f"{'└──' if last else '├──'} {k}")
            pre = "    " if last else "│   "
            if isinstance(v, dict):
                sub = list(v.items())
                for j, (kk, vv) in enumerate(sub):
                    lines.append(f"{pre}{'└──' if j == len(sub) - 1 else '├──'} {kk} = {vv}")
            else:
                lines.append(f"{pre}└── {v}")
        return "\n".join(lines)
