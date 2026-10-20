# Fiche d'identification — INCA 3

| Rubrique | Contenu |
|---|---|
| Nom | Étude individuelle nationale des consommations alimentaires 3 (INCA 3) |
| Producteur | Anses |
| Source | [data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3) (mise à jour du 28/01/2021) |
| Documentation | notice utilisateurs INCA 3 (janvier 2021), dans `data/raw/inca3/` |
| Période de recueil | 2014-2015 |
| Population de l'enquête | 5 855 individus de 0 à 79 ans, France métropolitaine |
| Méthode | 2 ou 3 rappels de 24 h non consécutifs |
| Population du projet | 2 121 adultes de 18-79 ans participants au volet consommation (Pop3) |
| Pondération utilisée | `pond_indiv_adu_pop3` (≈ 44,9 millions d'adultes représentés) |
| Clé individu | `NOIND` |
| Confidentialité | données pseudonymisées (numéro à la place de l'identité, âge en classes) |

## Fichiers utilisés

| Fichier | Lignes | Colonnes | Une ligne = |
|---|---|---|---|
| `description-indiv.csv` | 5 855 | 185 | un individu |
| `conso-compo-alim-vf-mad-datagouv2021.csv` | 256 301 (149 392 pour nos adultes) | 109 | un aliment consommé, avec sa composition pour 100 g |
| `apports-nut-alim.csv` | 4 114 | 108 | un individu (apports calculés par l'Anses) |

Format : CSV, séparateur `;`, encodage UTF-8, point décimal.

## Limites connues

- Seulement 2 ou 3 jours observés par personne : les moyennes sont fiables, les percentiles extrêmes moins (notice § 2.2.1).
- Données déclaratives : risque de sous-déclaration.
- Âge disponible uniquement en classes (18-44, 45-64, 65-79 ans).
