# `features` — linguistic feature extraction

Source: `src/delware_speech/features.py` (427 lines).
Replicates `reference_repo/speech/04_nlp_linguistic_feature_extraction.py` — the paper's
53-feature engine.
Unit tests: `tests/test_features.py`.

## What it does

Turns one block of participant speech into a flat dict of named numeric features:
lexical (POS counts/rates, diversity, richness), syntactic/structural (complexity,
clauses, passive voice, readability), and semantic/discourse (sentiment, cohesion,
deixis, tense). This is the module every quantitative claim in the paper rests on.

External models used: SpaCy `en_core_web_sm` (POS, dependencies, NER), NLTK
(tokenization, stopwords, WordNet, word frequencies), TextStat (readability, syllables,
reading time), TextBlob (sentiment).

## Constants

- `DISFLUENCIES` — filled pauses and fillers counted by `count_disfluencies`
  (*uh, um, oh, hm, er* variants plus *well, you know, like, so, actually, basically,
  i mean, alright, okay, right*).
- `SPATIAL_WORDS` — 24 locative terms for spatial deixis (*here, above, behind, left,
  top, inside*, …).
- `TEMPORAL_WORDS` — 15 temporal terms for temporal deixis (*now, then, before, always,
  soon*, …).

## Setup helpers (lazy loading)

- `get_nlp() -> spacy.language.Language` — loads `en_core_web_sm` once per process;
  auto-downloads the model if it is not installed.
- `get_stopwords() -> Set[str]` — NLTK English stopwords, downloading on `LookupError`.
- `get_common_words() -> Set[str]` — the 10,000 most frequent lowercase alphabetic
  Brown-corpus words (downloaded on first use) as the "common vocabulary" baseline for
  lexical sophistication; falls back to stopwords if the corpus is unavailable. (The
  reference approach of slicing NLTK's alphabetical `words` list is not frequency-ordered.)

## Feature math helpers

### `calculate_lexical_richness(tokens) -> Tuple[float, float, float]`

On alphabetic, non-stopword (content) tokens: returns `(ttr, brunets, honore)`:

- **TTR** — type-token ratio `V / N`.
- **Brunét's Index** — `V / N^0.165`.
- **Honoré's Statistic** — `100 · N · (ln N − ln V1)` with `V1` the hapax count;
  edge cases (no hapaxes, all hapaxes) return `0.0` / `100·N`.

### `calculate_hypernym_count(tokens) -> float`

Mean WordNet hypernym-tree depth (`synsets(w)[0].min_depth()`) across alphabetic
tokens that have synsets — a semantic-depth proxy. Returns `0.0` on any WordNet failure.

### `calculate_cohesion_score(sentences) -> float`

Halliday & Hasan cohesion proxy: for each pair of consecutive sentences, the Jaccard
overlap of their content-token sets; the score is the mean overlap. Fewer than two
sentences → `1.0`.

### `count_disfluencies(text) -> int`

Summed whole-word/phrase matches (`\b` boundaries, case-insensitive) of every `DISFLUENCIES`
entry. Substring matching, as in the reference script, would count *her* as `er`.

## Main entry point

### `extract_linguistic_features(text: str) -> Dict[str, Any]`

Empty/blank input returns the fully-keyed zero dict (`_empty_feature_dict`), so output
frames always share a schema. Otherwise:

1. SpaCy-tokenizes the text; NLTK sentence-tokenizes it (SpaCy sentence spans as
   fallback).
2. Computes POS counts/rates (verbs, nouns, pronouns, adjectives, adverbs,
   interjections, determiners, conjunctions (C+S), prepositions, auxiliaries,
   particles, numbers) and open/closed-class measures (`ocw`, `ccw`, `content_density`,
   `open_class_words_rate`).
3. Lexical block: `lexical_diversity` (unique lemmas / tokens), TTR, Brunét, Honoré,
   `hypernym_count`, `lexical_sophistication` (share of words outside the common
   vocabulary), `lexical_density` (content words / tokens), `function_word_count`.
4. Syntactic/structural block: `syntactic_complexity` — the paper's formula
   `(2·conjunctions + 2·pronouns + nouns + verbs) / total_counts`;
   `ref_r_real` = nouns/verbs; `dependent_clauses_per_sentence` (advcl, relcl, ccomp,
   xcomp, csubj, acl); `passive_voice_count`/`passive_voice_rate` (nsubjpass, auxpass,
   VBN); `word_count`, `sentence_count`, `mean_sentence_length`, `std_sentence_length`;
   `syllables`, `reading_time` (14.69 ms/char), and the five readability indices
   `dale_chall`, `flesch`, `coleman_liau_index`, `automated_readability_index`,
   `gunning_fog`.
5. Semantic/discourse block: `polarity`, `subjectivity` (TextBlob), `disfluencies`,
   `cohesion_score`, `personal_deixis_rate` (PRP/PRP$/WP/WP$), `spatial_deixis_rate`
   (LOC/GPE/FAC/ORG entities + `SPATIAL_WORDS`), `temporal_deixis_rate`
   (DATE/TIME entities + `TEMPORAL_WORDS`), and `past_tense_rate`,
   `present_tense_rate`, `future_tense_rate` (VBD/VBN vs VBP/VBZ/VBG/VB vs
   *will/shall/gonna/going to*, each over verbs+auxiliaries).

Every TextStat/TextBlob call is individually try-guarded — a failed metric yields `0.0`
for that field instead of aborting the extraction.

The returned dict has 63 keys (counts and their rates carried side by side); the
"53 features" of the paper is the feature *set* this implements, per its docstring and
the reference script.

## Notes for reviewers

- `_empty_feature_dict` is private but is the schema authority: its key list defines
  every column a processed dataset will have.
- Rates are computed over `total_counts` (sum of the counted POS classes, falling back
  to total tokens when no counted class appears) — check this when comparing numbers to
  the paper's tables.
