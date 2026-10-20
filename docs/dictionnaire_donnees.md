# Dictionnaire des données

Variables utilisées dans le projet (après chargement par `ChargeurINCA3`).

## Individus (une ligne par adulte)

| Variable | Définition | Type | Unité | Source |
|---|---|---|---|---|
| `NOIND` | identifiant de l'individu | entier | | INCA 3 |
| `sexe` | Homme / Femme | texte | | `sex_PS` (1 = homme, 2 = femme) |
| `classe_age` | 18-44, 45-64 ou 65-79 ans | texte | | `tage_PS` (codes 7, 8, 9) |
| `age_approx` | milieu de la classe d'âge (31, 55, 72) | entier | ans | calculé |
| `poids` | poids corporel déclaré | réel | kg | INCA 3 |
| `taille` | taille déclarée | réel | cm | INCA 3 |
| `ponderation` | poids de sondage | réel | | `pond_indiv_adu_pop3` |

## Consommations (une ligne par aliment consommé)

| Variable | Définition | Type | Unité | Source |
|---|---|---|---|---|
| `NUM_LIGNE` | identifiant de la ligne | entier | | INCA 3 |
| `R24_num` | numéro du jour de rappel (1 à 3) | entier | | INCA 3 |
| `R24_nombre` | nombre de jours de rappel de l'individu | entier | | INCA 3 |
| `R24_pond` | pondération du jour (semaine / week-end) | réel | | INCA 3 |
| `gpe_INCA3`, `groupe` | groupe d'aliments (code et libellé, 44 groupes) | entier / texte | | INCA 3 + notice |
| `aliment_code_INCA3` | code de l'aliment | entier | | INCA 3 |
| `aliment_libelle_INCA3` | nom de l'aliment | texte | | INCA 3 |
| `qte_conso` | quantité consommée | réel | g | INCA 3 |
| `qte_conso_pond` | quantité × `R24_pond` | réel | g | INCA 3 |

## Nutriments

Dans `conso-compo-alim` : teneur **pour 100 g** d'aliment. Après calcul : apport **par jour**.

| Variable | Nutriment | Unité | Colonne Anses (apports) |
|---|---|---|---|
| `aet` | énergie totale (alcool compris) | kcal | `nutriment1` |
| `proteines` | protéines | g | `nutriment3` |
| `glucides` | glucides | g | `nutriment4` |
| `fibres` | fibres | g | `nutriment8` |
| `lipides` | lipides | g | `nutriment10` |
| `alcool` | alcool | g | `nutriment28` |
| `calcium` | calcium | mg | `nutriment35` |
| `fer` | fer | mg | `nutriment37` |
| `vitamine_c` | vitamine C | mg | `nutriment51` |

## Variables calculées (notebook 04)

| Variable | Définition | Unité |
|---|---|---|
| `<nutriment>_1000kcal` | apport pour 1 000 kcal | unité / 1000 kcal |
| `mb` | métabolisme de base (Schofield) | kcal/j |
| `ratio_ae_mb` | apport énergétique / métabolisme de base | |
| `sous_declarant` | 1 si `ratio_ae_mb` < seuil de Goldberg | 0 / 1 |
