-- Modèle relationnel NutriHFr (SQLite)
--
--  individus 1──n journees 1──n consommations n──1 aliments
--                                   │
--                                   1──n composition n──1 nutriments
--  individus 1──n apports n──1 nutriments

DROP TABLE IF EXISTS apports;
DROP TABLE IF EXISTS composition;
DROP TABLE IF EXISTS consommations;
DROP TABLE IF EXISTS journees;
DROP TABLE IF EXISTS aliments;
DROP TABLE IF EXISTS nutriments;
DROP TABLE IF EXISTS individus;

CREATE TABLE individus (
    id_indiv     INTEGER PRIMARY KEY,
    sexe         TEXT NOT NULL,
    classe_age   TEXT NOT NULL,
    poids        REAL,
    taille       REAL,
    ponderation  REAL NOT NULL
);

CREATE TABLE journees (
    id_indiv    INTEGER NOT NULL REFERENCES individus(id_indiv),
    no_jour     INTEGER NOT NULL,
    poids_jour  REAL,                      -- R24_pond (semaine / week-end)
    PRIMARY KEY (id_indiv, no_jour)
);

CREATE TABLE aliments (
    code_aliment  INTEGER PRIMARY KEY,
    libelle       TEXT
);

CREATE TABLE nutriments (
    code_nutriment  TEXT PRIMARY KEY,
    libelle         TEXT,
    unite           TEXT
);

CREATE TABLE consommations (
    id_ligne         INTEGER PRIMARY KEY,
    id_indiv         INTEGER NOT NULL,
    no_jour          INTEGER NOT NULL,
    code_aliment     INTEGER NOT NULL REFERENCES aliments(code_aliment),
    groupe           TEXT,
    quantite_g       REAL CHECK (quantite_g >= 0),
    quantite_pond_g  REAL,
    FOREIGN KEY (id_indiv, no_jour) REFERENCES journees(id_indiv, no_jour)
);

-- composition de l'aliment consommé, pour 100 g (propre à chaque ligne)
CREATE TABLE composition (
    id_ligne        INTEGER NOT NULL REFERENCES consommations(id_ligne),
    code_nutriment  TEXT NOT NULL REFERENCES nutriments(code_nutriment),
    valeur_100g     REAL,
    PRIMARY KEY (id_ligne, code_nutriment)
);

-- résultat du pipeline : apport journalier moyen par individu
CREATE TABLE apports (
    id_indiv         INTEGER NOT NULL REFERENCES individus(id_indiv),
    code_nutriment   TEXT NOT NULL REFERENCES nutriments(code_nutriment),
    valeur_par_jour  REAL,
    PRIMARY KEY (id_indiv, code_nutriment)
);
