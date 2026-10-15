[Book index](README.md) › **1 · Overview**

# Overview — the study and the corpus

*Learn what the study claims, what data it uses, and what the pipeline produces.*

## The paper

This repository replicates and extends:

> Nyongesa et al. (2025). *Artificial intelligence-driven natural language processing
> for identifying linguistic patterns in Alzheimer's disease and mild cognitive
> impairment: A study of lexical, syntactic, and cohesive features of speech through
> picture description tasks.*

The full text is in the repository at `docs/paper/` (PDF plus extracted text), so every
claim in the docs can be checked against the source.

## The research question

Spontaneous speech changes measurably in Alzheimer's disease (AD) and mild cognitive
impairment (MCI): speakers become less fluent, less lexically rich, more
pronoun-heavy, and less cohesive. The study asks whether a systematic feature
engineering pass over picture-description speech can (a) quantify those differences
across diagnostic groups, (b) collapse dozens of linguistic measures into a small set
of interpretable domains, and (c) classify diagnosis from speech features alone — and
which features carry the most diagnostic signal.

## The corpus: DementiaBank Delaware

[DementiaBank](https://dementia.talkbank.org/) hosts transcript corpora of
speech-language samples from dementia research. The **Delaware** corpus contains
picture-description transcripts in CHAT format (the TalkBank `.cha` standard), with
participants in Control and MCI groups (the pipeline reads the workbook's `Control` and `MCI`
sheets; the processed data has 195 Control and 105 MCI participants), plus a demographics workbook
(`demo-test-fixed.xlsx`) with age, sex, education codes, MoCA scores, and diagnostic
classification per participant.

Three picture tasks anchor the study:

| Task | Canonical name here | What the participant does |
|------|---------------------|---------------------------|
| Cookie Theft | `Cookie` | Describes the classic "Cookie Theft" picture |
| Cat Rescue | `Cat` | Describes the cat-rescue picture |
| Coming & Going (Rockwell) | `Rockwell` | Describes the Rockwell painting |

The pipeline prefers Cookie Theft when a participant did several tasks — that priority
(Cookie > Cat > Rockwell) is a study design decision encoded in
`pipeline.select_unique_participants`.

## What the analysis does

1. **Extract speech.** Parse each transcript, keep participant utterances only, strip
   CHAT annotation while preserving natural disfluencies (*uh*, *um* — they are
   features here).
2. **Harmonize demographics.** Convert education codes to years, unify MoCA scores
   (with a blind-variant rescale), map classification codes to diagnoses.
3. **Extract the paper's 53-feature set** (63 output columns) per task record: lexical (POS rates, diversity,
   TTR, Brunét, Honoré, hypernym depth, sophistication, density), syntactic/structural
   (complexity, clauses, passive voice, five readability indices, sentence-length
   statistics), and semantic/discourse (sentiment, cohesion, deixis rates, tense
   rates, disfluencies).
4. **Compare groups.** ANOVA and Kruskal–Wallis with effect sizes (partial
   eta-squared, epsilon-squared, Cohen's d) and FDR/Bonferroni correction; ANCOVA
   adjusting for age and education.
5. **Correlate with cognition.** Pearson and Spearman correlations of every feature
   against MoCA, with regression slopes.
6. **Cluster the features.** Pearson correlation → distance `1 − R` → hierarchical
   complete-linkage and K-Means clustering, validated by elbow/silhouette, grouped
   labelled by a keyword heuristic with four candidate domain names (readability/lexical
   diversity; complexity/fluency/structure; sentiment/temporal/discourse; advanced
   syntactic/sophistication).

> [!WARNING]
> The domain-name heuristic currently collapses most clusters into one name, so read
> the member lists rather than the labels (see Known issues in
> `src/delware_speech/README.md`).
7. **Classify and rank.** Random Forest with 10-fold stratified CV (accuracy, Cohen's
   kappa, balanced accuracy), benchmarked against SVM (RBF) and Gradient Boosting,
   and a Gini-importance ranking of the most diagnostic features (top 20).
8. **Visualize.** Clustered correlation heatmap and t-SNE (Figure 3), task radar
   plots (Figure 4), violin distributions (Figure 5), MoCA regressions (Figure 6),
   and the importance bar chart.

## What the pipeline produces

| Directory | Contents | Written by |
|-----------|----------|------------|
| `data/` | `processed_features_all.csv/.xlsx` (every task record), `processed_features_unique.csv` (one row per participant) | processing stage |
| `results/` | `statistical_comparisons.csv`, `ancova_covariates_adjusted.csv`, `moca_correlations.csv`, `hierarchical_clusters_k4.csv`, `kmeans_clusters_k4.csv`, `cluster_validation_metrics.csv`, `feature_importance_rf.csv`, `model_benchmark_comparison.csv` | stats, clustering, importance stages |
| `figures/` | `Figure3_Correlation_Matrix.png`, `Figure3_tSNE_Clusters.png`, `Figure4_Task_Radar.png`, `Figure5_Feature_Violins.png`, `Figure6_MoCA_Regressions.png`, `Figure_Feature_Importance_Top20.png` | visualization stage |

## How this implementation relates to the original

The authors' original code — five numbered Python scripts and three R scripts — is
preserved in `reference_repo/speech/`. Each module in `src/delware_speech/` replaces
one of them (the mapping table is in `src/delware_speech/README.md`), with the
analysis logic kept faithful and the engineering improved: typed data classes, lazy
model loading, seeded randomness, per-file error containment, and unit tests per
module.

---

« Previous: [Book index](README.md) · Next: [2 · Architecture](architecture.md) »
