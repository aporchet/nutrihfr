# Data Quality Report

Généré automatiquement par `QualityChecker` (src/nutrihfr/quality.py).

| Dimension | Table | Contrôle | Résultat | Statut | Détail |
|---|---|---|---|---|---|
| Complétude | individus | % manquants poids_kg | 1.25 % | ALERTE |  |
| Complétude | individus | % manquants taille_cm | 0.50 % | ALERTE |  |
| Complétude | individus | % manquants poids_enquete | 0.00 % | OK |  |
| Complétude | consommations | % manquants quantite_g | 0.00 % | OK |  |
| Unicité | individus | id_indiv en double | 0 | OK |  |
| Unicité | consommations | lignes strictement identiques | 39 | ALERTE | même individu/jour/aliment/quantité |
| Unicité | aliments | code_aliment en double | 0 | OK |  |
| Validité | individus | âge < 0 | 0 | OK |  |
| Validité | consommations | quantité < 0 | 1 | KO |  |
| Validité | consommations | quantité = 0 | 0 | OK |  |
| Validité | individus | pondération <= 0 | 0 | OK |  |
| Validité | individus | sexe non codé | 0 | OK |  |
| Cohérence | individus | individus sans journée de consommation | 0 | OK |  |
| Cohérence | individus | plus de 7 jours de consommation | 0 | OK |  |
| Cohérence | individus | IMC hors [13 ; 70] | 2 | ALERTE |  |
| Intégrité référentielle | consommations | code_aliment absent de la nomenclature | 1 | ALERTE | [9999] |
| Intégrité référentielle | consommations | couverture composition (% lignes avec composition) | 100.00 % | OK |  |
| Intégrité référentielle | consommations | id_indiv inconnu | 0 | OK |  |
| Exactitude | consommations | quantité > 1500 g (solide) ou > 3000 g (boisson) | 1 | ALERTE |  |
| Exactitude | composition | somme des macronutriments > 105 g/100 g | 0 | OK |  |
| Homogénéité | nutriments | nutriments sans unité connue | 0 | OK |  |
| Homogénéité | consommations | unité des quantités | g (grammes) | OK | toutes les quantités INCA sont en grammes consommés |
| Traçabilité | indiv | empreinte description-indiv.csv | d1c334eff4ef | OK | 2000 lignes |
| Traçabilité | conso | empreinte conso-compo-alim.csv | 2caab4179dbd | OK | 97254 lignes |
| Traçabilité | apports | empreinte apports-nut-alim.csv | 083f8fa651ad | OK | 2000 lignes |
| Traçabilité | nomenclature | empreinte nomenclature.csv | 048fcfa80599 | OK | 48 lignes |

## Lignes écartées au nettoyage

| Motif | Lignes |
|---|---|
| aliment absent de la nomenclature (table d'exceptions) | 1 |
| doublon exact | 39 |
| quantité implausible | 1 |
| quantité manquante ou négative | 1 |

## Validation : apports recalculés vs apports fournis par l'Anses

| Nutriment | n | Corrélation | Écart relatif médian (%) | % individus écart < 5 % |
|---|---|---|---|---|
| energie_kcal | 2000 | 0.9999 | 0.00 | 99.9 |
| proteines_g | 2000 | 1.0000 | 0.00 | 99.9 |
| glucides_g | 2000 | 0.9999 | 0.00 | 99.9 |
| lipides_g | 2000 | 0.9999 | 0.00 | 99.7 |
| fibres_g | 2000 | 0.9999 | 0.01 | 99.8 |
| alcool_g | 2000 | 0.9998 | 0.03 | 83.3 |
| calcium_mg | 2000 | 1.0000 | 0.00 | 99.9 |
| fer_mg | 2000 | 0.9998 | 0.02 | 99.8 |
| vitc_mg | 2000 | 1.0000 | 0.00 | 99.9 |
