# Rapport qualité des données

Contrôles réalisés par `ControleQualite` (notebook 03) sur les 2 121 adultes et leurs 149 392 lignes de consommation. Le tableau complet est régénéré dans `outputs/tables/rapport_qualite.csv`.

| Dimension | Contrôle | Résultat | Statut |
|---|---|---|---|
| Complétude | poids corporel manquant | 5 individus | à vérifier |
| Complétude | taille, pondération manquantes | 0 | OK |
| Complétude | lignes sans composition nutritionnelle | 10 lignes (cyclamate, aspartame, réglisse) | à vérifier |
| Unicité | individus en double / lignes en double | 0 / 0 | OK |
| Validité | quantités nulles ou négatives | 0 | OK |
| Validité | compositions négatives | 0 | OK |
| Validité | sexe ou classe d'âge non codé | 0 | OK |
| Cohérence | jours observés ≠ `R24_nombre` | 0 | OK |
| Cohérence | adultes sans consommation | 0 | OK |
| Intégrité référentielle | consommation d'un individu inconnu | 0 | OK |
| Intégrité référentielle | groupe d'aliments inconnu | 0 | OK |
| Exactitude | quantité > 2 kg en une prise (max : 1,8 kg de bière) | 0 | OK |
| Exactitude | IMC hors [13 ; 70] | 0 | OK |
| Homogénéité | énergie Atwater ≈ énergie indiquée (écart < 10 %) | 96,7 % des lignes | OK |
| Traçabilité | lignes conservées / lues | 149 392 / 149 392 | OK |

## Traitement

- Aucune ligne supprimée : les données sont déjà nettoyées par l'Anses.
- Poids manquant : individu gardé, exclu seulement de l'analyse de sous-déclaration.
- Composition manquante : la ligne ne compte pas dans les apports (comme l'Anses).

## Validation du calcul des apports

Nos apports recalculés sont **identiques** à ceux publiés par l'Anses (`apports-nut-alim.csv`) pour les 9 nutriments et les 2 121 adultes (corrélation = 1, écart maximal < 0,001).
