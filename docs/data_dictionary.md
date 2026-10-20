# Dictionnaire de données

_Généré par le notebook 03._

| Table | Variable | Définition | Type | Unité | Source | % manquants |
|---|---|---|---|---|---|---|
| individus + apports | `id_indiv` | Identifiant pseudonymisé de l'individu | int64 |  | INCA3 NOIND | 0.0 |
| individus + apports | `sexe` | Sexe | str | Homme/Femme | INCA3 sex_PS recodé | 0.0 |
| individus + apports | `age` | Âge | float64 | années | INCA3 | 0.0 |
| individus + apports | `classe_age_src` | Classe d'âge fournie par l'Anses | int64 | code | INCA3 tage_PS | 0.0 |
| individus + apports | `poids_kg` | Poids corporel | float64 | kg | INCA3 | 1.25 |
| individus + apports | `taille_cm` | Taille | float64 | cm | INCA3 | 0.5 |
| individus + apports | `poids_enquete` | Pondération d'enquête (adultes) | float64 |  | INCA3 pond_indiv_adu_pop2 | 0.0 |
| individus + apports | `enquete` | Enquête d'origine | str |  | pipeline | 0.0 |
| individus + apports | `classe_age` | Classe d'âge du projet | str |  | pipeline (18-24, 25-44, 45-64, 65-79) | 0.0 |
| individus + apports | `n_jours` | Nombre de journées de consommation retenues | int64 | jours | pipeline | 0.0 |
| individus + apports | `energie_kcal` | Énergie : apport journalier moyen (ou teneur selon la table) | float64 | kcal/j | pipeline | 0.0 |
| individus + apports | `proteines_g` | Protéines : apport journalier moyen (ou teneur selon la table) | float64 | g/j | pipeline | 0.0 |
| individus + apports | `glucides_g` | Glucides : apport journalier moyen (ou teneur selon la table) | float64 | g/j | pipeline | 0.0 |
| individus + apports | `lipides_g` | Lipides : apport journalier moyen (ou teneur selon la table) | float64 | g/j | pipeline | 0.0 |
| individus + apports | `fibres_g` | Fibres alimentaires : apport journalier moyen (ou teneur selon la table) | float64 | g/j | pipeline | 0.0 |
| individus + apports | `alcool_g` | Alcool : apport journalier moyen (ou teneur selon la table) | float64 | g/j | pipeline | 0.0 |
| individus + apports | `calcium_mg` | Calcium : apport journalier moyen (ou teneur selon la table) | float64 | mg/j | pipeline | 0.0 |
| individus + apports | `fer_mg` | Fer : apport journalier moyen (ou teneur selon la table) | float64 | mg/j | pipeline | 0.0 |
| individus + apports | `vitc_mg` | Vitamine C : apport journalier moyen (ou teneur selon la table) | float64 | mg/j | pipeline | 0.0 |
| individus + apports | `bmr_kcal` | Métabolisme de base estimé (Schofield) | float64 | kcal/j | pipeline | 1.25 |
| individus + apports | `ei_bmr` | Rapport apport énergétique / métabolisme de base | float64 |  | pipeline | 1.25 |
| individus + apports | `seuil_goldberg` | Seuil de Goldberg (Black 2000) selon le nombre de jours | float64 |  | pipeline | 0.0 |
| individus + apports | `sous_declarant` | Sous-déclarant de l'énergie (EI/BMR < seuil) | boolean | booléen | pipeline | 1.25 |
| individus + apports | `proteines_g_per1000kcal` | Protéines pour 1 000 kcal | float64 | g/1000 kcal | pipeline | 0.0 |
| individus + apports | `glucides_g_per1000kcal` | Glucides pour 1 000 kcal | float64 | g/1000 kcal | pipeline | 0.0 |
| individus + apports | `lipides_g_per1000kcal` | Lipides pour 1 000 kcal | float64 | g/1000 kcal | pipeline | 0.0 |
| individus + apports | `fibres_g_per1000kcal` | Fibres alimentaires pour 1 000 kcal | float64 | g/1000 kcal | pipeline | 0.0 |
| individus + apports | `alcool_g_per1000kcal` | Alcool pour 1 000 kcal | float64 | g/1000 kcal | pipeline | 0.0 |
| individus + apports | `calcium_mg_per1000kcal` | Calcium pour 1 000 kcal | float64 | mg/1000 kcal | pipeline | 0.0 |
| individus + apports | `fer_mg_per1000kcal` | Fer pour 1 000 kcal | float64 | mg/1000 kcal | pipeline | 0.0 |
| individus + apports | `vitc_mg_per1000kcal` | Vitamine C pour 1 000 kcal | float64 | mg/1000 kcal | pipeline | 0.0 |
| individus + apports | `pct_ae_proteines` | Part de l'apport énergétique due aux proteines | float64 | % | pipeline | 0.0 |
| individus + apports | `pct_ae_glucides` | Part de l'apport énergétique due aux glucides | float64 | % | pipeline | 0.0 |
| individus + apports | `pct_ae_lipides` | Part de l'apport énergétique due aux lipides | float64 | % | pipeline | 0.0 |
| consommations | `id_conso` | Identifiant de la ligne de consommation | int64 |  | pipeline | 0.0 |
| consommations | `id_jour` | Identifiant de la journée (id_indiv_no_jour) | str |  | pipeline | 0.0 |
| consommations | `id_indiv` | Identifiant pseudonymisé de l'individu | int64 |  | INCA3 NOIND | 0.0 |
| consommations | `code_aliment` | Code de l'aliment (nomenclature INCA 3) | int64 |  | INCA3 | 0.0 |
| consommations | `quantite_g` | Quantité consommée | float64 | g | INCA3 | 0.0 |
| aliments | `code_aliment` | Code de l'aliment (nomenclature INCA 3) | int64 |  | INCA3 | 0.0 |
| aliments | `libelle` | Libellé de l'aliment | str |  | INCA3 nomenclature | 0.0 |
| aliments | `groupe` | Groupe d'aliments | str |  | INCA3 nomenclature | 0.0 |
| composition | `code_aliment` | Code de l'aliment (nomenclature INCA 3) | int64 |  | INCA3 | 0.0 |
| composition | `code_nutriment` | Code canonique du nutriment | str |  | config.NUTRIENTS | 0.0 |
| composition | `valeur_100g` | Teneur du nutriment pour 100 g d'aliment | float64 | unité du nutriment | INCA3 conso-compo-alim | 0.0 |
| composition | `source` | Origine de la valeur de composition | str |  | pipeline | 0.0 |
