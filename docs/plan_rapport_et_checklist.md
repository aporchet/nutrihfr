# Plan du rapport final (5-10 pages) et check-list des attendus

## A. Plan du rapport final (≈ 8 pages)

| § | Contenu | Pages | Sources dans le dépôt |
|---|---|---|---|
| 1 | **Introduction** : contexte INCA, question scientifique, Q1-Q6 | 0,5 | notebook 01 §1, README |
| 2 | **Données** : sources, choix INCA 3 (+ INCA 2 en comparaison), Ciqual et version, population 18-79 ans, volumétrie | 1 | `docs/fiches_identification.md` |
| 3 | **Data engineering** : pipeline (schéma), modèle relationnel, règles de nettoyage, valeurs manquantes, RGPD | 1,5 | notebook 02, `sql/schema.sql` |
| 4 | **Qualité et validation** : 8 dimensions (tableau résumé), recalcul vs apports Anses, Atwater | 1 | `docs/data_quality_report.md`, notebook 03 |
| 5 | **Méthodes** : pondérations, IC, régression pondérée, ratio des moyennes, Goldberg, décomposition intra/inter | 1 | notebooks 04-05 |
| 6 | **Résultats** Q1 à Q6 : 1 figure + 1 phrase « à retenir » par question, avec n, pondération, IC | 2,5 | `outputs/figures`, `outputs/tables` |
| 7 | **Discussion** : choix des métriques, robustesse (avec/sans sous-déclarants, pondéré ou non), reproductibilité, traçabilité, limites | 1 | notebook 05, README §6 |
| 8 | **Conclusion et perspectives** (apport habituel NCI/SPADE, mapping par embeddings, plan de sondage complet) | 0,5 | notebook 06 |

Conseils : une figure = un message (titre-phrase) ; toujours indiquer *n*, « pondéré » et l'IC 95 % ; citer l'Anses selon la notice.

## B. Arguments pour la discussion (et l'oral)

**Choix des métriques**
- Moyenne pondérée : estimation de la population, comparable aux publications Anses ; la médiane et les percentiles complètent pour les distributions asymétriques.
- Densité pour 1 000 kcal : compare la *qualité* de l'alimentation indépendamment de la quantité mangée.
- Ratio des moyennes pour les contributions : répond à « d'où vient le nutriment consommé par la population », parts qui somment à 100 %, stable chez les petits mangeurs.

**Validation et robustesse**
- Recalcul des apports Anses (corrélation, écart relatif) : valide jointures, formule et agrégation.
- Atwater : valide la cohérence de la table de composition.
- Sensibilité : avec/sans sous-déclarants, PAL 1,45-1,75, pondéré/non pondéré, IC linéarisation vs bootstrap.

**Reproductibilité** : pipeline relançable en une commande, configuration centralisée, graine fixe, `requirements.txt`, tests pytest + intégration continue GitHub Actions.

**Traçabilité** : SHA-256 des fichiers bruts, journal `run_log.json`, table `exclusions` avec motifs, lignage des résultats avec commit Git (annexe C).

## C. Check-list des critères de réussite (annexe A)

| Critère | Où ? | ✓ |
|---|---|---|
| Sources documentées | fiches d'identification, README §3 | ☐ |
| Transformations traçables | table `exclusions`, `run_log.json`, `Lineage` | ☐ |
| Versions enregistrées | SHA-256, `CIQUAL_VERSION`, commit Git | ☐ |
| Unités harmonisées | `config.NUTRIENTS`, test 2 | ☐ |
| Taux de valeurs manquantes | rapport qualité (complétude) | ☐ |
| Doublons contrôlés | rapport qualité (unicité) | ☐ |
| Valeurs aberrantes | rapport qualité (exactitude), `DataCleaner` | ☐ |
| Intégrité référentielle | rapport qualité, clés SQLite, test 3 | ☐ |
| Couverture du mapping | notebook 06 | ☐ |
| Apports calculés, unités vérifiées | `IntakeCalculator`, tests 4-5 | ☐ |
| Nutriments documentés | `docs/data_dictionary.md` | ☐ |
| Cas particuliers (0 g, « traces », poids manquant) | `to_number`, test 5, Goldberg « inclassable » | ☐ |
| Descriptif, âge/sexe, IC, pondérations | notebook 04 | ☐ |
| Hypothèses statistiques documentées | notebook 04 (en-tête), `stats.py` | ☐ |
| Code versionné, environnement, tests, relançable, README | dépôt GitHub | ☐ |

## D. Les 7 livrables (annexe B)

1. README → `README.md`
2. Data dictionary → `docs/data_dictionary.md` (généré par le notebook 03)
3. Data Quality Report → `docs/data_quality_report.md` (généré par le pipeline)
4. Pipeline Python → `src/nutrihfr/` + `scripts/run_pipeline.py`
5. Analyse statistique → notebooks 04 et 05 (+ 06 bonus)
6. Dashboard → `app/dashboard.py`
7. Rapport final → à rédiger selon le plan A
