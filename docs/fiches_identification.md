# Fiches d'identification des jeux de données

_Générées par le notebook 01 (mode `synthetic`)._

## INCA 3

| Rubrique | Contenu |
|---|---|
| Producteur | Anses |
| URL | https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3 |
| Période | 2014-2015 |
| Population | 0-79 ans, France métropolitaine (≈ 5 800 individus, à confirmer dans la notice) |
| Méthode de recueil | 3 rappels de 24 h non consécutifs (adultes) ; enregistrements pour les enfants |
| Granularité | ligne = un aliment consommé, un individu, un jour |
| Clé(s) | NOIND (+ nojour) |
| Licence | non précisée sur data.gouv.fr : respecter les règles de citation de la notice utilisateurs |
| Version | mise à jour du 28/01/2021 |
| Confidentialité (RGPD) | données pseudonymisées (identifiant NOIND, pas de nom) |
| Limites connues | sous-déclaration possible, 3 jours seulement, composition figée à la version Ciqual utilisée par l'Anses |

**Volumétrie et qualité (calculées)**

| Fichier | Lignes | Colonnes | Taille (Mo) | % cellules vides | Lignes dupliquées | SHA-256 |
|---|---|---|---|---|---|---|
| apports-nut-alim.csv | 2,000 | 10 | 0.13 | 0.0 | 0 | `083f8fa651ad` |
| conso-compo-alim.csv | 97,254 | 13 | 5.36 | 0.0 | 39 | `2caab4179dbd` |
| description-indiv.csv | 2,000 | 7 | 0.07 | 0.2 | 0 | `d1c334eff4ef` |
| nomenclature.csv | 48 | 3 | 0.00 | 0.0 | 0 | `048fcfa80599` |

## INCA 2

| Rubrique | Contenu |
|---|---|
| Producteur | AFSSA / Anses |
| URL | https://www.data.gouv.fr/datasets/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-2-3 |
| Période | 2006-2007 |
| Population | 3-79 ans, France métropolitaine (≈ 2 600 adultes) |
| Méthode de recueil | carnet alimentaire sur 7 jours consécutifs |
| Granularité | individu (apports) / aliment-jour (consommations) |
| Clé(s) | identifiant individu (nomen) |
| Licence | Licence Ouverte (Etalab) |
| Version | mise en ligne 24/09/2014 |
| Confidentialité (RGPD) | données pseudonymisées |
| Limites connues | méthode et nomenclature différentes d'INCA 3 |

**Volumétrie et qualité (calculées)**

| Fichier | Lignes | Colonnes | Taille (Mo) | % cellules vides | Lignes dupliquées | SHA-256 |
|---|---|---|---|---|---|---|
| Table_apports_nut.csv | 1,500 | 9 | 0.07 | 0.0 | 0 | `7645bc015cf7` |
| Table_indiv.csv | 1,500 | 4 | 0.02 | 0.0 | 0 | `8bed9b075b71` |

## Ciqual

| Rubrique | Contenu |
|---|---|
| Producteur | Anses |
| URL | https://ciqual.anses.fr |
| Période | Ciqual 2020 |
| Population | ≈ 3 000 aliments génériques |
| Méthode de recueil | compilation d'analyses et de données bibliographiques |
| Granularité | ligne = un aliment, valeurs pour 100 g |
| Clé(s) | alim_code |
| Licence | Licence Ouverte (Etalab) |
| Version | Ciqual 2020 (une version 2025 existe : documenter le choix) |
| Confidentialité (RGPD) | sans objet (pas de données personnelles) |
| Limites connues | valeurs manquantes ou texte ('traces', '< x'), versions successives non comparables à 100 % |

**Volumétrie et qualité (calculées)**

| Fichier | Lignes | Colonnes | Taille (Mo) | % cellules vides | Lignes dupliquées | SHA-256 |
|---|---|---|---|---|---|---|
| ciqual_2020.csv | 48 | 12 | 0.00 | 0.0 | 0 | `651b8eef2ae7` |
