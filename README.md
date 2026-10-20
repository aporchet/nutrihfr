# NutriHFr — Consommations alimentaires et apports nutritionnels des adultes en France

Projet de Data Science de bout en bout sur les enquêtes **INCA 3** (Anses, 2014-2015) et **INCA 2** (2006-2007) :
de la question scientifique au dashboard, avec un pipeline Python reproductible, une base SQL, des contrôles qualité et des tests automatisés.

---

## 1. Contexte

Les études INCA de l'Anses décrivent ce que mangent les personnes vivant en France métropolitaine. Croisées avec des tables de composition nutritionnelle des aliments, elles permettent d'estimer les apports en énergie et en nutriments de la population.

## 2. Problématique

> **Comment se caractérisent les consommations alimentaires et les apports nutritionnels des adultes en France, comment varient-ils selon l'âge et le sexe, et quels aliments y contribuent le plus ?**

| | Question | Notebook |
|---|---|---|
| Q1 | Distribution de l'apport énergétique journalier | 04 |
| Q2 | Différences d'apports entre hommes et femmes | 04 |
| Q3 | Évolution des apports avec l'âge | 04 |
| Q4 | Densité nutritionnelle (pour 1 000 kcal) | 04 |
| Q5 | Aliments contributeurs (protéines, calcium, fer, fibres, vitamine C) | 04 |
| Q6 | Variabilité interindividuelle (ex. femmes 25-44 ans) | 04 |
| Bonus | Profils alimentaires, diversité, INCA 2 vs INCA 3, mapping INCA ↔ Ciqual | 06 |

Périmètre : **adultes de 18 à 79 ans**.

## 3. Sources de données

| Source | Rôle | Lien |
|---|---|---|
| INCA 3 (Anses, 2014-2015) | source principale : individus, consommations, composition, apports | [data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3) |
| INCA 2 (2006-2007) | comparaison agrégée (bonus), jamais fusionnée avec INCA 3 | [data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-2-3) |
| Ciqual (Anses) | contrôle Atwater, mapping (bonus) | [ciqual.anses.fr](https://ciqual.anses.fr) |

Fiches d'identification détaillées : [`docs/fiches_identification.md`](docs/fiches_identification.md).
INCA 1 est écarté (méthode et nomenclature incompatibles) ; INCA 2 et INCA 3 sont analysés **séparément** car leurs méthodes de recueil diffèrent (carnet 7 jours vs 3 rappels de 24 h).

## 4. Méthodologie

```
data/raw (CSV INCA)
   │  Inca3Loader       lecture robuste, renommage canonique, filtre 18-79 ans
   ▼
QualityChecker          8 dimensions de qualité  ──► docs/data_quality_report.md
   ▼
DataCleaner             doublons, quantités < 0 ou implausibles, aliments inconnus ──► table exclusions
   ▼
IntakeCalculator        quantité/100 × teneur → somme par jour → moyenne des jours par individu
   ▼
flag_underreporters     critère de Goldberg (Schofield + seuil de Black 2000)
   ▼
NutriDatabase (SQLite)  modèle relationnel avec clés et contraintes ──► data/processed/nutrihfr.sqlite
   ▼
stats.py                moyennes / percentiles pondérés, IC 95 %, régression pondérée
   ▼
notebooks 04-06, dashboard Streamlit
```

Points méthodologiques :
- **Pondérations d'enquête** utilisées pour toutes les moyennes et tous les percentiles.
- **Sous-déclaration** : critère de Goldberg, analyses avec et sans sous-déclarants (notebook 05).
- **Apport d'un jour vs apport habituel** : décomposition de la variance intra / inter-individuelle (Q6).
- **Contributions** : ratio des moyennes pondéré (comparé à la moyenne des ratios).
- **Validation** : les apports recalculés sont comparés aux apports fournis par l'Anses.

## 5. Résultats

*À compléter avec les vraies données (les figures se trouvent dans `outputs/figures/`, les tableaux dans `outputs/tables/`).*

| Question | Résultat principal |
|---|---|
| Q1 | apport énergétique moyen : … kcal/j (IC 95 % …) |
| Q2 | … |
| Q3 | … |
| Q4 | … |
| Q5 | … |
| Q6 | … |

## 6. Limites

- Recueil déclaratif sur 3 jours : sous-déclaration et apports d'un jour ≠ apports habituels.
- IC calculés sans les strates / grappes du plan de sondage (légèrement trop étroits).
- Composition figée à la version de table utilisée par l'Anses pour INCA 3 ; Ciqual plus récent non directement substituable sans mapping.
- Comparaison INCA 2 / INCA 3 confondue avec les changements de méthode.
- Critère de Goldberg dépendant d'une hypothèse de niveau d'activité physique.

---

## Structure du dépôt

```
nutrihfr/
├── README.md
├── requirements.txt
├── src/nutrihfr/          code du pipeline (classes)
│   ├── config.py          ← SEUL fichier à adapter aux vraies données
│   ├── loader.py          chargement INCA 3, INCA 2, Ciqual
│   ├── quality.py         contrôle qualité et nettoyage
│   ├── intake.py          calcul des apports, Goldberg, Atwater
│   ├── database.py        base SQLite
│   ├── stats.py           statistiques pondérées
│   ├── lineage.py         traçabilité des résultats
│   ├── pipeline.py        orchestration de bout en bout
│   └── viz.py             style graphique
├── sql/schema.sql         modèle relationnel
├── notebooks/             01 → 06, à exécuter dans l'ordre
├── tests/test_pipeline.py tests de l'annexe D (pytest)
├── app/dashboard.py       dashboard Streamlit
├── scripts/               run_pipeline.py, make_synthetic_data.py
├── docs/                  fiches, dictionnaire, rapport qualité, plan du rapport
├── data/                  raw / processed (non versionnés)
└── outputs/               figures et tableaux
```

## Installation et reproduction

```bash
git clone <url-du-repo> && cd nutrihfr
python -m venv .venv && source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt

python scripts/make_synthetic_data.py   # (optionnel) données de démonstration
python scripts/run_pipeline.py          # pipeline complet
pytest -v                               # tests automatisés
jupyter lab notebooks/                  # analyses
streamlit run app/dashboard.py          # dashboard
```

### Passer aux vraies données INCA

1. Télécharger depuis data.gouv.fr : `description-indiv.csv`, `conso-compo-alim.csv`, `apports-nut-alim.csv`, `nomenclature.csv` (+ la notice PDF) → `data/raw/inca3/`. Idem pour INCA 2 → `data/raw/inca2/` et l'export Ciqual (CSV ou XLSX) → `data/raw/ciqual/`.
2. Dans `src/nutrihfr/config.py`, remplacer la valeur par défaut `"synthetic"` par `"real"` dans la ligne `MODE = ...`.
3. Exécuter le notebook **01** : la cellule « vérification » liste les colonnes à corriger dans `config.py` (lignes `# A VERIFIER`).
4. Exécuter le notebook **02** : il indique si la composition est « pour 100 g » ou « pour la portion ».
5. Relancer `python scripts/run_pipeline.py`, `pytest`, puis les notebooks 03 à 06.

## Traçabilité et reproductibilité

- **Données** : empreinte SHA-256 de chaque fichier brut, versions et journal de chargement dans `data/processed/run_log.json` et dans la table SQL `sources`.
- **Transformations** : chaque ligne écartée est conservée avec son motif (table `exclusions`).
- **Résultats** : chaque résultat clé peut être exporté avec son lignage (`Lineage`, annexe C), incluant le commit Git.
- **Environnement** : `requirements.txt` ; graine aléatoire fixée.
- **Tests** : `tests/test_pipeline.py`, exécutés automatiquement par GitHub Actions à chaque push.

## Confidentialité

Les données INCA sont pseudonymisées mais restent des données personnelles de santé : les fichiers bruts ne sont pas versionnés, seuls des résultats agrégés sont publiés, le dashboard masque les groupes de moins de 30 personnes.

## Références

- Anses (2017). *Étude individuelle nationale des consommations alimentaires 3 (INCA 3)*. Rapport d'expertise collective.
- Anses. Table de composition nutritionnelle des aliments Ciqual.
- Black A.E. (2000). Critical evaluation of energy intake using the Goldberg cut-off for energy intake:basal metabolic rate. *Int J Obes*, 24, 1119-1130.
- Schofield W.N. (1985). Predicting basal metabolic rate, new standards and review of previous work. *Hum Nutr Clin Nutr*, 39C, 5-41.
