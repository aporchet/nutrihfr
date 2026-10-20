"""Création et alimentation de la base SQLite à partir des tables canoniques."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from . import config as C

TABLE_ORDER = ["sources", "individus", "journees", "aliments", "nutriments",
               "composition", "consommations", "exclusions", "apports_individuels"]


class NutriDatabase:
    def __init__(self, path: Path = C.DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def create_schema(self):
        with self.connect() as con:
            con.executescript(C.SCHEMA_SQL.read_text(encoding="utf-8"))

    def load(self, tables: dict[str, pd.DataFrame]):
        """Insère les tables dans l'ordre des dépendances (parents avant enfants).
        Les contraintes (clés, CHECK) du schéma sont vérifiées à l'insertion."""
        self.create_schema()
        with self.connect() as con:
            for name in TABLE_ORDER:
                if name not in tables:
                    continue
                df = tables[name]
                cols = [r[1] for r in con.execute(f"PRAGMA table_info({name})")]
                df = df[[c for c in cols if c in df.columns]]
                df.to_sql(name, con, if_exists="append", index=False)

    def check_integrity(self) -> pd.DataFrame:
        with self.connect() as con:
            return pd.read_sql("PRAGMA foreign_key_check", con)

    def query(self, sql: str) -> pd.DataFrame:
        with self.connect() as con:
            return pd.read_sql(sql, con)

    def counts(self) -> pd.DataFrame:
        rows = []
        with self.connect() as con:
            for t in TABLE_ORDER:
                n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                rows.append({"table": t, "n_lignes": n})
        return pd.DataFrame(rows)
