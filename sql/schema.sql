-- Modèle relationnel NutriHFr (SQLite)
-- individus 1--n journees 1--n consommations n--1 aliments 1--n composition n--1 nutriments

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS apports_individuels;
DROP TABLE IF EXISTS exclusions;
DROP TABLE IF EXISTS consommations;
DROP TABLE IF EXISTS composition;
DROP TABLE IF EXISTS journees;
DROP TABLE IF EXISTS individus;
DROP TABLE IF EXISTS aliments;
DROP TABLE IF EXISTS nutriments;
DROP TABLE IF EXISTS sources;

CREATE TABLE sources (
    enquete     TEXT NOT NULL,
    table_src   TEXT NOT NULL,
    fichier     TEXT NOT NULL,
    sha256      TEXT NOT NULL,
    n_lignes    INTEGER,
    PRIMARY KEY (enquete, table_src)
);

CREATE TABLE individus (
    id_indiv       INTEGER PRIMARY KEY,
    enquete        TEXT NOT NULL,
    sexe           TEXT NOT NULL CHECK (sexe IN ('Homme', 'Femme')),
    age            REAL CHECK (age >= 0),
    classe_age     TEXT,
    poids_kg       REAL,
    taille_cm      REAL,
    poids_enquete  REAL NOT NULL CHECK (poids_enquete > 0),
    n_jours        INTEGER
);

CREATE TABLE journees (
    id_jour   TEXT PRIMARY KEY,
    id_indiv  INTEGER NOT NULL REFERENCES individus(id_indiv),
    no_jour   INTEGER NOT NULL
);

CREATE TABLE aliments (
    code_aliment  INTEGER PRIMARY KEY,
    libelle       TEXT,
    groupe        TEXT
);

CREATE TABLE nutriments (
    code_nutriment  TEXT PRIMARY KEY,
    libelle         TEXT NOT NULL,
    unite           TEXT NOT NULL
);

CREATE TABLE composition (
    code_aliment    INTEGER NOT NULL REFERENCES aliments(code_aliment),
    code_nutriment  TEXT    NOT NULL REFERENCES nutriments(code_nutriment),
    valeur_100g     REAL,
    source          TEXT,
    PRIMARY KEY (code_aliment, code_nutriment)
);

CREATE TABLE consommations (
    id_conso      INTEGER PRIMARY KEY,
    id_jour       TEXT    NOT NULL REFERENCES journees(id_jour),
    id_indiv      INTEGER NOT NULL REFERENCES individus(id_indiv),
    code_aliment  INTEGER NOT NULL REFERENCES aliments(code_aliment),
    quantite_g    REAL    NOT NULL CHECK (quantite_g >= 0)
);

-- lignes écartées au nettoyage (pas de clés étrangères : on garde même les codes inconnus)
CREATE TABLE exclusions (
    id_conso      INTEGER,
    id_jour       TEXT,
    id_indiv      INTEGER,
    code_aliment  INTEGER,
    quantite_g    REAL,
    motif         TEXT
);

-- résultat du pipeline : apport journalier moyen par individu (format long)
CREATE TABLE apports_individuels (
    id_indiv        INTEGER NOT NULL REFERENCES individus(id_indiv),
    code_nutriment  TEXT    NOT NULL REFERENCES nutriments(code_nutriment),
    valeur          REAL,
    PRIMARY KEY (id_indiv, code_nutriment)
);

CREATE INDEX idx_conso_jour ON consommations(id_jour);
CREATE INDEX idx_conso_aliment ON consommations(code_aliment);
