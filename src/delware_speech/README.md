# `delware_speech` — source map

Python re-implementation of the analysis pipeline in Nyongesa et al. (2025),
*"AI-driven NLP for identifying linguistic patterns in Alzheimer's disease and mild
cognitive impairment: lexical, syntactic, and cohesive features of speech through
picture description tasks"*, run on the DementiaBank **Delaware** corpus.

This file is the map of the package: what each file does, which functions it exposes,
and **why the file was created** (which paper stage or original R/Python reference script
it replaces). Read it top-to-bottom when checking the code; deeper per-function detail
lives in `docs/reference/<module>.md`, and the narrative walkthrough lives in `book/`.

## File map at a glance

| File | Role in the pipeline | Replaces (original paper scripts) | Task |
|------|----------------------|-----------------------------------|------|
| `__init__.py` | Package identity and version | — | — |
| `chat_reader.py` | Parse `.cha` CHAT transcripts into participant speech per picture task | `01_convert_cha_to_txt.py` | T1 |
| `demographics.py` | Harmonize the demographics workbook (education codes → years, MoCA, diagnosis) | `02_demographics_summary_processing.py` | T1 |
| `features.py` | Extract the paper's 53-feature set (63 output columns) from one speech text | `04_nlp_linguistic_feature_extraction.py` | T2 |
| `pipeline.py` | Orchestrate parsing + demographics + features into participant datasets | `03_process_text_files.py` | T3 |
| `statistical_analysis.py` | Group comparisons, ANCOVA, MoCA correlations with effect sizes | `05_linguistic_statistical_analysis.py` | T4 |
| `clustering.py` | Correlate features, cluster them, validate k, name clinical domains | `Cluster_Analysis.R` | T5 |
| `importance.py` | Random Forest Gini importance + RF/SVM/GB benchmarking for diagnosis | `Importance_Features.R` | T5 |
| `visualization.py` | Publication figures (heatmap, t-SNE, radar, violin, regression, importance) | `t-SNE_PLOTS_.R` + plot code in the R scripts | T5 |

Tasks T1–T6 are the implementation plan in `tasks.json` at the repository root.

Data flows in the order of the table: transcripts + workbook → `chat_reader` →
`demographics` → (merged by `pipeline`) → `features` → one of {`statistical_analysis`,
`clustering`, `importance`} → `visualization`. `main.py` at the repository root wires all
of it behind a CLI.

---

## `__init__.py`

**Purpose.** Marks the directory as an importable Python package and carries the package
name and version string (`delware_speech`, `0.1.0`).

**Why this file exists.** So the pipeline can be imported as a library
(`from delware_speech.pipeline import process_dataset`) rather than only run as a script,
which is what makes every module independently testable under `tests/`.

**Contents.** Docstring and `__version__` only — no code.

---

## `chat_reader.py`

**Purpose.** Turn raw DementiaBank CHAT (`.cha`) transcript files into structured
participant speech, grouped by picture-description task.

**Public API.**

- `ParticipantHeader` — dataclass with participant metadata parsed from the `@ID:` line:
  `pid`, `corpus`, `age` (years), `sex`, `diagnosis`, `mmse_moca`, `raw_header`.
- `ParsedTranscript` — dataclass holding `file_id`, `file_path`, `participant_header`, and
  `tasks` (dict of task name → list of cleaned utterances). Methods:
  - `get_task_text(task_name)` — all participant utterances of one task, joined.
  - `get_all_picture_tasks()` — text for each canonical picture task present.
- `CANONICAL_PICTURE_TASKS` — mapping of canonical task names (`Cookie`, `Cat`,
  `Rockwell`) to the CHAT `@G:` aliases the Delaware corpus actually uses (including the
  misspelling `rackwell`).
- `clean_chat_utterance(text)` — strip CHAT markup (timestamps `22301_28488`, bracket
  codes `[//]`, `[+ exc]`, fragment codes `&~`, `@q` postcodes, pause symbols) while
  keeping spoken words and natural disfluencies — filled pauses coded `&-uh` / `&-um` keep
  their word (only the `&-` marker is dropped), because they are features, not noise, in
  this study. Not stripped (known issue): `(.)` pause markers, `xxx` unintelligible
  tokens, and parenthesised completions like `(be)cause`.
- `parse_age(age_str)` — CHAT age `87;00.` (years;months) → float years.
- `parse_participant_header(cha_content, fallback_id)` — read the participant `@ID:` line
  into a `ParticipantHeader`.
- `parse_cha_file(file_path)` — the entry point: one `.cha` file → `ParsedTranscript`.
  Handles continuation lines (tab-indented) and assigns utterances to the current `@G:`
  group, defaulting to `"Default"`.

**Why this file exists.** The paper's unit of analysis is the participant's speech on a
standardized picture task, but DementiaBank ships transcripts in CHAT format mixed with
investigator speech and transcription codes. This file is the single place that knows the
file format, so every later stage works on clean text and never sees CHAT markup.

**Checked by.** `tests/test_chat_reader.py`.

---

## `demographics.py`

**Purpose.** Load and harmonize the Delaware demographics workbook
(`demo-test-fixed.xlsx`) into one clean row per participant.

**Public API.**

- `EDUCATION_CODE_TO_YEARS` — the paper's mapping of categorical education codes 0–10 to
  approximate years of schooling (e.g. `3 → 12.0` high-school graduate, `7 → 16.0`
  bachelor's, `10 → 21.0` doctorate).
- `CLASSIFICATION_CODE_TO_NAME` — numeric classification to diagnosis name
  (`1 → Control`, `2 → MCI`, `3 → PossibleAD`, `4 → Other`).
- `map_education_to_years(code)` — code → years, `None` for missing/unknown.
- `map_sex(code_or_str)` — standardize the workbook's 1/2/F/M encodings to
  `female` / `male` / passthrough / `unknown`.
- `parse_numeric(val)` — float-or-None coercion for score cells.
- `load_delaware_demographics(excel_path)` — the entry point: reads the `Control` and
  `MCI` sheets, harmonizes columns into `ID`, `Record_ID`, `Visit_Number`, `Age`, `Sex`,
  `Education_Code`, `Education_Years`, `MoCA`, `Diagnosis`, `Source_Sheet`. MoCA falls
  back to the blind variant rescaled from the 22-point to the 30-point scale; duplicate
  IDs keep the first record.

**Why this file exists.** The statistical stages (ANCOVA, MoCA correlations) need
education in *years* and a single cognitive score per participant, while the workbook
stores education as codes, two separate MoCA columns, and mixed encodings. This file is
the only place that knows the workbook's layout, so the rest of the code deals with one
tidy DataFrame.

**Checked by.** `tests/test_demographics.py`.

---

## `features.py`

**Purpose.** Extract the paper's linguistic feature set from one block of participant
speech — the heart of the study.

**Public API.**

- `DISFLUENCIES`, `SPATIAL_WORDS`, `TEMPORAL_WORDS` — the paper's word lists for
  disfluency counting and spatial/temporal deixis.
- `get_nlp()` — lazy-load the SpaCy `en_core_web_sm` model (auto-downloads on first use).
- `get_stopwords()` / `get_common_words()` — lazy NLTK resources for content-word and
  lexical-sophistication calculations (common words = the 10,000 most frequent
  Brown-corpus words).
- `calculate_lexical_richness(tokens)` — TTR, Brunét's Index (`V / N^0.165`), Honoré's
  statistic on content words.
- `calculate_hypernym_count(tokens)` — mean WordNet hypernym-tree depth of alphabetic
  tokens (first synset each; stopwords included).
- `calculate_cohesion_score(sentences)` — Halliday & Hasan cohesion as mean Jaccard
  overlap of consecutive sentence token sets.
- `count_disfluencies(text)` — total filled-pause / filler occurrences, matched as whole
  words/phrases (`\b` boundaries), not substrings.
- `extract_linguistic_features(text)` — the entry point: one speech text → flat dict of
  named numeric features, in three paper groups:
  - *Lexical* — POS counts and rates (verbs, nouns, pronouns, …), open/closed-class word
    measures, lexical diversity, TTR, Brunét, Honoré, hypernym depth, sophistication,
    density, function-word count.
  - *Syntactic & structural* — syntactic complexity (the paper's
    `(2·conj + 2·pron + noun + verb) / total` formula), dependent clauses per sentence,
    passive-voice measures, `ref_r_real` (noun/verb ratio), sentence-length statistics,
    syllables, reading time, five readability indices (Dale-Chall, Flesch, Coleman-Liau,
    ARI, Gunning Fog).
  - *Semantic & discourse* — sentiment polarity/subjectivity (TextBlob), disfluencies,
    cohesion, personal/spatial/temporal deixis rates, past/present/future tense rates.
  Empty input returns a fully-keyed zero dict (`_empty_feature_dict`), so downstream
  frames always have the same columns. Readability/textstat/TextBlob calls are individually
  guarded — one failing metric never aborts extraction.

**Why this file exists.** Every claim in the paper rests on these numbers being
reproducible. The file concentrates all NLP-model usage (SpaCy POS/dependency/NER, NLTK,
TextStat, TextBlob) in one lazy-loaded module so the rest of the pipeline stays
model-free, and so feature semantics have exactly one definition to review.

**Checked by.** `tests/test_features.py`.

---

## `pipeline.py`

**Purpose.** Batch orchestration: walk the corpus, join demographics to transcripts, run
feature extraction per task, and reduce to one row per participant.

**Public API.**

- `map_to_canonical_task(task_name)` — CHAT `@G:` tag → canonical picture task, or `None`
  for non-picture chatter.
- `process_single_cha(cha_path, demographics_df=None)` — one transcript → one record per
  canonical picture task found in it, with demographics merged in (transcript `@ID:` data
  as fallback when the workbook has no match) plus the `Participant_Text` that produced
  the features.
- `process_dataset(corpus_root, demographics_excel=None, show_progress=True)` — the entry
  point: recursively finds `*.cha` under the corpus root (or its `transcript/` folder),
  processes each with per-file error logging, returns the all-records DataFrame.
- `select_unique_participants(df_all, priority=("Cookie", "Cat", "Rockwell"))` — the
  paper's participant-level dataset: keep one task row per participant
  (`Record_ID`, else the ID prefix before `-`), preferring Cookie Theft > Cat Rescue >
  Rockwell and the earliest visit.

**Why this file exists.** The paper reports both an *all-tasks* dataset and a
*unique-participants* dataset; the priority rule (Cookie first) is a study design
decision, not a generic utility. Keeping it here — rather than inside the analysis
stages — makes both datasets reproducible from one function pair and keeps
`main.py` a thin CLI.

**Checked by.** `tests/test_pipeline.py`.

---

## `statistical_analysis.py`

**Purpose.** The paper's inferential statistics: do linguistic features differ across
diagnostic groups, and do they track cognition?

**Public API.**

- `compute_cohens_d(group1, group2)` — Cohen's d with pooled SD.
- `perform_group_comparisons(df, features, group_col="Diagnosis")` — per feature:
  one-way ANOVA (F, p, partial eta-squared), Kruskal–Wallis (H, p, epsilon-squared),
  Cohen's d when exactly two groups, per-group means/SDs, plus Bonferroni and
  Benjamini–Hochberg FDR correction across features.
- `perform_ancova(df, features, group_col="Diagnosis", covariates=("Age", "Education_Years"))`
  — OLS per feature controlling for age and education years (`Feature ~ C(Diagnosis) +
  Age + Education_Years`), reporting the whole-model F, the first group dummy's coefficient and p, and model R²
  (the dummy is the full group effect only with two groups), with FDR correction. Requires ≥10 complete rows per feature.
- `compute_cognitive_correlations(df, features, score_col="MoCA")` — per feature:
  Pearson r (with p, R², FDR-corrected), Spearman rho, and the OLS slope/intercept/SE
  against the cognitive score.

**Why this file exists.** The paper's Results tables are exactly these three outputs
(group differences, covariate-adjusted differences, cognition correlations), each with
effect sizes and multiple-testing correction — the statistics, not just raw p-values,
are the paper's contribution. Centralizing them keeps the correction rules (FDR +
Bonferroni) consistent across every table.

**Checked by.** `tests/test_statistical_analysis.py`.

---

## `clustering.py`

**Purpose.** Replicates `Cluster_Analysis.R`: discover which linguistic features
co-vary, group them, and validate the grouping — the paper's feature-domain analysis.

**Public API.**

- `EXCLUDE_NON_FEATURE_COLS` — identifiers/demographics/count columns excluded from
  clustering so only linguistic features cluster.
- `get_numeric_feature_columns(df)` — numeric, non-excluded, nonzero-variance columns.
- `compute_correlation_and_distance(df, feature_cols)` — Pearson correlation matrix
  between features and the distance matrix `D = 1 − R` (diagonal zeroed).
- `cluster_features_hierarchical(corr_matrix, dist_matrix, n_clusters=4, method="complete")`
  — hierarchical complete-linkage clustering on the distance matrix; returns
  Feature → Cluster assignments.
- `cluster_features_kmeans(corr_matrix, n_clusters=4, random_state=42)` — K-Means on the
  correlation profiles; returns assignments plus the silhouette score.
- `evaluate_cluster_elbow_and_silhouette(corr_matrix, k_range=range(2, 7), random_state=42)`
  — inertia and silhouette per k, the elbow-curve validation behind the paper's choice
  of four clusters.
- `assign_cluster_domain_names(cluster_df)` — map each cluster to an interpretive
  clinical domain label (e.g. *"Readability & Lexical Diversity"*) from its member
  features' names (first-match-wins keyword rules — a heuristic, see Known issues).

**Why this file exists.** The paper argues the 50+ features collapse into a small number
of interpretable domains; that claim needs the exact pipeline (Pearson distance →
complete-linkage *and* K-Means, cross-validated by elbow/silhouette) to be inspectable.
This file is the faithful Python port of the original R script, seeded
(`random_state=42`) for reproducibility.

**Checked by.** `tests/test_clustering_importance.py`.

---

## `importance.py`

**Purpose.** Replicates `Importance_Features.R`: which features best predict diagnosis,
and how well do classifiers separate groups?

**Public API.**

- `prepare_classification_data(df, target_col="Diagnosis", feature_cols=None)` — build
  the X/y matrices: drop missing targets, drop `other`/`unknown` classes, median-impute
  missing feature values.
- `evaluate_classifier_cv(clf, X, y, n_splits=10, random_state=42)` — stratified 10-fold
  CV returning mean/SD accuracy, Cohen's kappa, and balanced accuracy. The
  `StandardScaler` is fitted **inside each fold** to avoid leakage.
- `compute_feature_importance_rf(X, y, feature_names, n_estimators=100, random_state=42)`
  — Random Forest mean-decrease-in-Gini importances, ranked, scaled to percentages.
- `benchmark_all_models(X, y, random_state=42)` — the paper's model comparison table:
  Random Forest vs SVM (RBF) vs Gradient Boosting under identical 10-fold CV.

**Why this file exists.** The paper's headline result is a ranking of the most
diagnostic linguistic features (top 20) plus evidence that tree ensembles separate
diagnostic groups. This file reproduces that ranking and benchmark with fixed
seeds (importances come from an in-sample fit on all rows, not from CV), and is the only module that trains models — keeping ML concerns out of the
statistics module.

**Checked by.** `tests/test_clustering_importance.py`.

---

## `visualization.py`

**Purpose.** Publication-grade figures matching the paper's Figures 3–6 and the
importance chart, replacing the original R plotting scripts (including
`t-SNE_PLOTS_.R`) with Matplotlib/Seaborn.

**Public API.**

- `CLUSTER_PALETTE`, `DIAGNOSIS_PALETTE` — fixed color schemes matching the paper's
  aesthetics (purple/blue/orange/red clusters; blue/orange/red diagnosis groups).
  `DIAGNOSIS_PALETTE` is currently unused by any plot.
- `plot_cluster_correlation_matrix(corr_matrix, cluster_df, output_path)` — Figure 3:
  correlation heatmap ordered by cluster so domain blocks are visible.
- `plot_tsne_clusters(corr_matrix, cluster_df, output_path, random_state=42)` — Figure 3
  (right): 2-D t-SNE projection of the feature correlation profiles, colored by cluster.
- `plot_feature_importance(importance_df, output_path, top_n=20)` — top-N Random Forest
  importance bar chart with value labels.
- `plot_violin_features(df, features_to_plot, output_path, group_col="Diagnosis")` —
  Figure 5: violin distributions of selected features across diagnostic groups.
- `plot_cognitive_regressions(df, features_to_plot, output_path, score_col="MoCA",
  group_col="Diagnosis")` — Figure 6: scatter + regression of features vs MoCA, each
  panel annotated with its Pearson r.
- `plot_task_radar(df, features_to_plot, output_path, task_col="Task",
  group_col="Diagnosis")` — Figure 4(b): per-task radar plots of normalized feature
  means, one polar subplot per picture task.

All functions save to PNG (300 dpi) via the non-interactive `Agg` backend and create
their output directory, so they work headless and never display a window.

**Why this file exists.** The figures are how the paper's claims are read; this module
reproduces each one from pipeline outputs with deterministic settings, so a reviewer can
regenerate every figure of the paper from the processed data with one command.

**Checked by.** Not covered by unit tests (plotting code); verified by the figure files
it produces under `figures/` during end-to-end runs (task T6).

---

## Known issues

Found in review; fixed items are marked. Open items are documented, not changed.

- **Fixed:** `clean_chat_utterance` used to delete `&-uh`/`&-um` fillers; `count_disfluencies`
  used to count substrings (`er` in *her*); `get_common_words` used an alphabetical word list.
  Re-run `--process` to refresh `data/` and `results/` after these fixes.
- `assign_cluster_domain_names` is a first-match keyword heuristic. On the committed outputs
  all four hierarchical clusters got the same label and K-Means produced two distinct names, so
  the paper's four named domains are not reproduced.
- `perform_ancova` reports the whole-model F and only the first group dummy's p — correct for
  two groups (Control/MCI today), not for three or more.
- `perform_group_comparisons` zips filtered group data with the unfiltered group list, so a
  group with no values for a feature would shift the `Mean_`/`SD_` labels.
- `passive_voice_*` counts every `VBN` tag and double-counts `nsubjpass` + `auxpass`.
- Brunét's index and Honoré's statistic use the reference script's formulas, which differ from
  the textbook definitions; kept for fidelity with the authors' code.
- `process_single_cha` defaults `Diagnosis` to `Control` when neither workbook nor header has one.
- `compute_feature_importance_rf` is fitted on all rows; importance is not cross-validated.
- `(.)`, `xxx` and `(be)cause` survive CHAT cleaning and slightly inflate token counts.

---

## How the package is wired together

`main.py` (repository root) composes the modules in five stages, each togglable by CLI
flag: **process** (`chat_reader` + `demographics` + `pipeline`) → **stats**
(`statistical_analysis`) → **cluster** (`clustering`) → **importance**
(`importance.py`) → **visualize** (`visualization.py`). Cached intermediate datasets are
written to `data/`, statistical tables to `results/`, and figures to `figures/`.

For per-function reference pages see `docs/reference/`; for the narrative tour see
`book/architecture.md`.
