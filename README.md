# NutriHFr — Apports nutritionnels des adultes en France (INCA 3)

Projet de Data Science (cours) : de la question scientifique aux résultats, à partir de l'étude **INCA 3** de l'Anses (2014-2015).

## Contexte et problématique

> Comment se caractérisent les apports nutritionnels des adultes en France, comment varient-ils selon l'âge et le sexe, et quels aliments y contribuent le plus ?

Questions traitées : Q1 apport énergétique · Q2 différences hommes/femmes · Q3 effet de l'âge · Q4 densité nutritionnelle · Q5 aliments contributeurs (protéines, calcium, fer, fibres, vitamine C) · Q6 variabilité entre individus.

## Données

- **INCA 3** (Anses) : [data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3)
- Population : **2 121 adultes de 18-79 ans** ayant réalisé 2 ou 3 rappels de 24 h, pondérés pour représenter environ 45 millions d'adultes.
- Fiche détaillée : [`docs/fiche_donnees.md`](docs/fiche_donnees.md) · variables : [`docs/dictionnaire_donnees.md`](docs/dictionnaire_donnees.md)

## Méthode

1. **Chargement** des 3 fichiers INCA 3 et sélection des adultes Pop3 (`ChargeurINCA3`).
2. **Contrôle qualité** sur 8 dimensions (`ControleQualite`) → [`docs/rapport_qualite.md`](docs/rapport_qualite.md).
3. **Calcul des apports** (`CalculApports`), méthode de l'Anses :
   apport journalier = Σ (`qte_conso_pond` / 100 × composition pour 100 g) / nombre de jours.
   **Validation** : nos apports sont identiques à ceux publiés par l'Anses.
4. **Base SQLite** (modèle relationnel dans `sql/schema.sql`).
5. **Statistiques pondérées** : moyennes, IC 95 %, percentiles, régression ; contributions par « ratio des moyennes » ; sous-déclaration par le critère de Goldberg.

## Principaux résultats

| | Résultat (moyennes pondérées) |
|---|---|
| Q1 | Apport énergétique moyen : **2 102 kcal/j** (IC 95 % : 2 048-2 157) ; 2 438 kcal/j chez les hommes, 1 787 chez les femmes |
| Q2 | Les femmes ont des apports plus faibles que les hommes pour tous les nutriments étudiés : de −11 % (vitamine C) à −27 % (énergie, fer), et −70 % pour l'alcool |
| Q3 | L'apport énergétique diminue avec l'âge chez les deux sexes |
| Q4 | Pour 1 000 kcal, les femmes ont une alimentation plus riche en vitamine C (+21 %), calcium (+11 %) et fibres (+11 %) |
| Q5 | Calcium : fromages, yaourts et laits ; vitamine C : fruits, jus et légumes ; fibres : pain raffiné, légumes et fruits |
| Q6 | Forte dispersion entre individus, en partie gonflée par le faible nombre de jours observés |
| Robustesse | Exclure les sous-déclarants augmente les apports de 8 à 21 % ; la pondération change les moyennes de moins de 6 % |

## Limites

- 2-3 jours par personne : moyennes fiables, percentiles extrêmes moins (pas de modélisation de l'apport habituel).
- Données déclaratives : sous-déclaration probable.
- Âge connu seulement en classes ; intervalles de confiance calculés sans les strates du plan de sondage (un peu trop étroits).

## Organisation du dépôt

```
nutrihfr/
├── README.md
├── requirements.txt
├── data/raw/inca3/        fichiers INCA 3 + notice (non versionnés)
├── data/processed/        résultats du pipeline + base SQLite (non versionnés)
├── docs/                  fiche des données, dictionnaire, rapport qualité
├── notebooks/
│   ├── 01_donnees.ipynb            problématique, sources, population
│   ├── 02_data_engineering.ipynb   chargement, exploration, pondérations, SQL, RGPD
│   ├── 03_qualite.ipynb            contrôles qualité, calcul et validation des apports
│   ├── 04_analyses.ipynb           questions Q1 à Q6, sous-déclaration, robustesse
│   └── 05_tests.ipynb              tests du pipeline (annexe D)
├── outputs/               figures et tableaux produits par les notebooks
├── scripts/run_pipeline.py  relance tout le pipeline en une commande
├── sql/schema.sql         modèle relationnel
└── src/nutrihfr/
    ├── config.py          chemins, fichiers, variables, groupes d'aliments
    ├── pipeline.py        ChargeurINCA3, ControleQualite, CalculApports, base SQLite
    └── stats.py           statistiques pondérées, contributions, Goldberg
```

## Reproduire

```bash
conda create -n nutrihfr python=3.11 -y
conda activate nutrihfr
pip install -r requirements.txt
```

1. Télécharger les fichiers INCA 3 sur data.gouv.fr dans `data/raw/inca3/` : `description-indiv.csv`, `conso-compo-alim-vf-mad-datagouv2021.csv`, `apports-nut-alim.csv`.
2. Lancer `python scripts/run_pipeline.py`, puis les notebooks dans l'ordre (01 → 05).

## Confidentialité

Données pseudonymisées mais personnelles (santé) : elles ne sont pas publiées sur GitHub, et seuls des résultats agrégés sont présentés.
