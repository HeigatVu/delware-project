"""Linguistic feature extraction module implementing 53 features from Nyongesa et al. (2025).

Aggregates lexical, syntactic, structural, and semantic/discourse features
using SpaCy, NLTK, TextStat, and TextBlob.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Set, Tuple

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
import spacy
from textblob import TextBlob
import textstat

# Lazy-loaded NLP models
_NLP = None
_STOPWORDS: Set[str] = set()
_COMMON_WORDS: Set[str] = set()

DISFLUENCIES = [
    "uh", "uhh", "um", "umm", "oh", "ohh", "hm", "hmm", "er", "erm",
    "well", "you know", "like", "so", "actually", "basically", "i mean",
    "alright", "okay", "right",
]

SPATIAL_WORDS = {
    "here", "there", "where", "this", "that", "these", "those",
    "above", "below", "behind", "in", "on", "under", "next", "near",
    "left", "right", "top", "bottom", "inside", "outside", "up", "down",
}

TEMPORAL_WORDS = {
    "now", "then", "yesterday", "today", "tomorrow", "soon", "later",
    "before", "after", "always", "never", "sometimes", "often", "early", "late",
}


def get_nlp() -> spacy.language.Language:
    """Get or initialize SpaCy English model."""
    global _NLP
    if _NLP is None:
        try:
            _NLP = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not downloaded
            from spacy.cli import download
            download("en_core_web_sm")
            _NLP = spacy.load("en_core_web_sm")
    return _NLP


def get_stopwords() -> Set[str]:
    """Get NLTK english stopwords."""
    global _STOPWORDS
    if not _STOPWORDS:
        try:
            _STOPWORDS = set(stopwords.words("english"))
        except LookupError:
            nltk.download("stopwords")
            _STOPWORDS = set(stopwords.words("english"))
    return _STOPWORDS


def get_common_words() -> Set[str]:
    """Get common words for lexical sophistication calculation."""
    global _COMMON_WORDS
    if not _COMMON_WORDS:
        try:
            from nltk.corpus import words as nltk_words
            # Use top subset of frequent words or standard wordnet lemmas
            _COMMON_WORDS = set(nltk_words.words()[:10000])
        except Exception:
            _COMMON_WORDS = get_stopwords()
    return _COMMON_WORDS


def calculate_lexical_richness(tokens: List[str]) -> Tuple[float, float, float]:
    """Calculate Type-Token Ratio (TTR), Brunét's Index, and Honoré's Statistic."""
    stops = get_stopwords()
    content_tokens = [w.lower() for w in tokens if w.isalpha() and w.lower() not in stops]
    n = len(content_tokens)
    if n == 0:
        return 0.0, 0.0, 0.0

    v = len(set(content_tokens))
    ttr = v / n

    # Brunét's Index: W = V / (N ** 0.165)
    brunets = v / (n ** 0.165) if n > 0 else 0.0

    # Honoré's Statistic: R = 100 * (N * (ln N - ln V1)) where V1 = hapaxes
    fdist = FreqDist(content_tokens)
    hapaxes = len(fdist.hapaxes())
    if hapaxes > 0 and hapaxes < n:
        honore = 100.0 * (n * (math.log(n) - math.log(hapaxes)))
    elif hapaxes == n:
        honore = 100.0 * n
    else:
        honore = 0.0

    return ttr, brunets, honore


def calculate_hypernym_count(tokens: List[str]) -> float:
    """Calculate mean hypernym tree depth for noun and verb tokens via WordNet."""
    try:
        depths = []
        for word in tokens:
            if word.isalpha():
                synsets = wordnet.synsets(word.lower())
                if synsets:
                    # Minimum path to root hypernym
                    depths.append(synsets[0].min_depth())
        return float(np.mean(depths)) if depths else 0.0
    except Exception:
        return 0.0


def calculate_cohesion_score(sentences: List[str]) -> float:
    """Calculate Halliday & Hasan discourse cohesion across consecutive sentences."""
    if len(sentences) < 2:
        return 1.0

    stops = get_stopwords()
    tokenized_sents = [
        set(w.lower() for w in word_tokenize(s) if w.isalpha() and w.lower() not in stops)
        for s in sentences
    ]

    overlaps = []
    for i in range(len(tokenized_sents) - 1):
        s1, s2 = tokenized_sents[i], tokenized_sents[i + 1]
        union = s1.union(s2)
        if union:
            jaccard = len(s1.intersection(s2)) / len(union)
            overlaps.append(jaccard)
        else:
            overlaps.append(0.0)

    return float(np.mean(overlaps)) if overlaps else 0.0


def count_disfluencies(text: str) -> int:
    """Count disfluencies and filled pauses."""
    lower = text.lower()
    return sum(lower.count(d) for d in DISFLUENCIES)


def extract_linguistic_features(text: str) -> Dict[str, Any]:
    """Extract all 53 linguistic features from a participant's speech text.

    Returns a flat dictionary of named numerical features.
    """
    if not isinstance(text, str) or not text.strip():
        # Return zeroed dictionary with full keys
        return _empty_feature_dict()

    clean_text = text.strip()
    words = clean_text.split()
    word_cnt = len(words)
    if word_cnt == 0:
        return _empty_feature_dict()

    nlp = get_nlp()
    doc = nlp(clean_text)
    total_tokens = len(doc)
    if total_tokens == 0:
        return _empty_feature_dict()

    # Sentences
    try:
        sentences = sent_tokenize(clean_text)
    except Exception:
        sentences = [s.text for s in doc.sents]
    if not sentences:
        sentences = [clean_text]
    num_sentences = len(sentences)
    sentence_lens = [len(s.split()) for s in sentences]
    mean_sent_len = float(np.mean(sentence_lens))
    std_sent_len = float(np.std(sentence_lens))

    # POS Tag counts
    pos_counts = Counter(token.pos_ for token in doc)
    tag_counts = Counter(token.tag_ for token in doc)

    verbs = pos_counts.get("VERB", 0)
    nouns = pos_counts.get("NOUN", 0)
    pronouns = pos_counts.get("PRON", 0)
    adjectives = pos_counts.get("ADJ", 0)
    adverbs = pos_counts.get("ADV", 0)
    interjections = pos_counts.get("INTJ", 0)
    determiners = pos_counts.get("DET", 0)
    conjunctions = pos_counts.get("CCONJ", 0) + pos_counts.get("SCONJ", 0)
    prepositions = pos_counts.get("ADP", 0)
    auxiliary_verbs = pos_counts.get("AUX", 0)
    particles = pos_counts.get("PART", 0)
    numbers = pos_counts.get("NUM", 0)

    total_counts = verbs + nouns + pronouns + adjectives + adverbs + interjections + \
        determiners + conjunctions + prepositions + auxiliary_verbs + particles + numbers
    if total_counts == 0:
        total_counts = total_tokens

    # Open and Closed Class Words
    ocw = verbs + nouns + adjectives + adverbs
    ccw = max(0, total_counts - ocw)
    content_density = ocw / ccw if ccw > 0 else float(ocw)
    open_class_rate = ocw / total_counts if total_counts > 0 else 0.0

    # Rates
    verbs_rate = verbs / total_counts
    nouns_rate = nouns / total_counts
    pronouns_rate = pronouns / total_counts
    adjectives_rate = adjectives / total_counts
    adverbs_rate = adverbs / total_counts
    interjections_rate = interjections / total_counts
    determiners_rate = determiners / total_counts
    conjunctions_rate = conjunctions / total_counts
    prepositions_rate = prepositions / total_counts
    auxiliary_verbs_rate = auxiliary_verbs / total_counts
    particles_rate = particles / total_counts
    numbers_rate = numbers / total_counts

    # Lexical Diversity
    alpha_tokens = [t for t in doc if t.is_alpha]
    unique_lemmas = {t.lemma_.lower() for t in alpha_tokens}
    lexical_diversity = len(unique_lemmas) / total_tokens if total_tokens > 0 else 0.0

    # NLTK tokenization for richness
    raw_tokens = word_tokenize(clean_text)
    ttr, brunets, honore = calculate_lexical_richness(raw_tokens)
    hypernym_cnt = calculate_hypernym_count(raw_tokens)

    # Lexical Density (content words / total tokens)
    stops = get_stopwords()
    content_words = [t for t in alpha_tokens if t.text.lower() not in stops]
    lexical_density = len(content_words) / total_tokens if total_tokens > 0 else 0.0
    function_word_count = sum(1 for t in alpha_tokens if t.text.lower() in stops)

    # Lexical Sophistication (words not in top common vocabulary)
    common_words = get_common_words()
    advanced_words = sum(1 for t in alpha_tokens if t.text.lower() not in common_words)
    lexical_sophistication = advanced_words / len(alpha_tokens) if alpha_tokens else 0.0

    # Syntactic Complexity (Nyongesa formula)
    syntactic_complexity = (2 * conjunctions + 2 * pronouns + nouns + verbs) / total_counts if total_counts > 0 else 0.0
    ref_r_real = nouns / verbs if verbs > 0 else float(nouns)

    # Dependency Parsing: Dependent Clauses and Passive Voice
    dep_clauses = sum(1 for token in doc if token.dep_ in ("advcl", "relcl", "ccomp", "xcomp", "csubj", "acl"))
    dep_clauses_per_sentence = dep_clauses / num_sentences if num_sentences > 0 else 0.0

    passive_constructions = sum(1 for token in doc if token.dep_ in ("nsubjpass", "auxpass") or token.tag_ == "VBN")
    passive_voice_rate = passive_constructions / total_tokens if total_tokens > 0 else 0.0

    # Readability Metrics
    try:
        dale_chall = float(textstat.dale_chall_readability_score(clean_text))
    except Exception:
        dale_chall = 0.0
    try:
        flesch = float(textstat.flesch_reading_ease(clean_text))
    except Exception:
        flesch = 0.0
    try:
        coleman_liau = float(textstat.coleman_liau_index(clean_text))
    except Exception:
        coleman_liau = 0.0
    try:
        ari = float(textstat.automated_readability_index(clean_text))
    except Exception:
        ari = 0.0
    try:
        gunning_fog = float(textstat.gunning_fog(clean_text))
    except Exception:
        gunning_fog = 0.0
    try:
        syllables = float(textstat.syllable_count(clean_text))
    except Exception:
        syllables = float(word_cnt)
    try:
        reading_time = float(textstat.reading_time(clean_text, ms_per_char=14.69))
    except Exception:
        reading_time = float(word_cnt) * 0.3

    # Sentiment & Cohesion
    try:
        tb = TextBlob(clean_text)
        polarity = float(tb.sentiment.polarity)
        subjectivity = float(tb.sentiment.subjectivity)
    except Exception:
        polarity = 0.0
        subjectivity = 0.0

    cohesion_score = calculate_cohesion_score(sentences)
    disfluency_cnt = count_disfluencies(clean_text)

    # Deixis Rates
    # Personal Deixis: PRP, PRP$, WP, WP$
    p_deixis_count = sum(1 for t in doc if t.tag_ in ("PRP", "PRP$", "WP", "WP$"))
    personal_deixis_rate = p_deixis_count / total_tokens if total_tokens > 0 else 0.0

    # Spatial Deixis: LOC, GPE, FAC, ORG entities or spatial words
    s_entities = sum(1 for ent in doc.ents if ent.label_ in ("LOC", "GPE", "FAC", "ORG"))
    s_words = sum(1 for t in doc if t.text.lower() in SPATIAL_WORDS)
    spatial_deixis_rate = (s_entities + s_words) / total_tokens if total_tokens > 0 else 0.0

    # Temporal Deixis: DATE, TIME entities or temporal words
    t_entities = sum(1 for ent in doc.ents if ent.label_ in ("DATE", "TIME"))
    t_words = sum(1 for t in doc if t.text.lower() in TEMPORAL_WORDS)
    temporal_deixis_rate = (t_entities + t_words) / total_tokens if total_tokens > 0 else 0.0

    # Verb Tense Rates
    total_verbs_all = max(1, verbs + auxiliary_verbs)
    past_verbs = tag_counts.get("VBD", 0) + tag_counts.get("VBN", 0)
    pres_verbs = (
        tag_counts.get("VBP", 0) + tag_counts.get("VBZ", 0) +
        tag_counts.get("VBG", 0) + tag_counts.get("VB", 0)
    )
    fut_markers = sum(
        1 for t in doc if t.text.lower() in ("will", "shall", "gonna") or
        (t.text.lower() == "going" and "to" in [c.text.lower() for c in t.children])
    )

    past_tense_rate = past_verbs / total_verbs_all
    present_tense_rate = pres_verbs / total_verbs_all
    future_tense_rate = fut_markers / total_verbs_all

    return {
        # Lexical
        "verbs": verbs,
        "verbs_rate": verbs_rate,
        "nouns": nouns,
        "nouns_rate": nouns_rate,
        "pronouns": pronouns,
        "pronouns_rate": pronouns_rate,
        "adjectives": adjectives,
        "adjectives_rate": adjectives_rate,
        "adverbs": adverbs,
        "adverbs_rate": adverbs_rate,
        "interjections": interjections,
        "interjections_rate": interjections_rate,
        "determiners": determiners,
        "determiners_rate": determiners_rate,
        "conjunctions": conjunctions,
        "conjunctions_rate": conjunctions_rate,
        "prepositions": prepositions,
        "prepositions_rate": prepositions_rate,
        "auxiliary_verbs": auxiliary_verbs,
        "auxiliary_verbs_rate": auxiliary_verbs_rate,
        "particles": particles,
        "particles_rate": particles_rate,
        "numbers": numbers,
        "numbers_rate": numbers_rate,
        "total_counts": total_counts,
        "ocw": ocw,
        "ccw": ccw,
        "content_density": content_density,
        "open_class_words_rate": open_class_rate,
        "lexical_diversity": lexical_diversity,
        "ttr": ttr,
        "brunets_index": brunets,
        "honore_statistic": honore,
        "hypernym_count": hypernym_cnt,
        "lexical_sophistication": lexical_sophistication,
        "lexical_density": lexical_density,
        "function_word_count": function_word_count,

        # Syntactic & Structural
        "syntactic_complexity": syntactic_complexity,
        "dependent_clauses_per_sentence": dep_clauses_per_sentence,
        "passive_voice_count": passive_constructions,
        "passive_voice_rate": passive_voice_rate,
        "ref_r_real": ref_r_real,
        "word_count": word_cnt,
        "sentence_count": num_sentences,
        "mean_sentence_length": mean_sent_len,
        "std_sentence_length": std_sent_len,
        "syllables": syllables,
        "reading_time": reading_time,
        "dale_chall": dale_chall,
        "flesch": flesch,
        "coleman_liau_index": coleman_liau,
        "automated_readability_index": ari,
        "gunning_fog": gunning_fog,

        # Semantic & Discourse
        "polarity": polarity,
        "subjectivity": subjectivity,
        "disfluencies": disfluency_cnt,
        "cohesion_score": cohesion_score,
        "personal_deixis_rate": personal_deixis_rate,
        "spatial_deixis_rate": spatial_deixis_rate,
        "temporal_deixis_rate": temporal_deixis_rate,
        "past_tense_rate": past_tense_rate,
        "present_tense_rate": present_tense_rate,
        "future_tense_rate": future_tense_rate,
    }


def _empty_feature_dict() -> Dict[str, float]:
    """Return zeroed features when text is empty."""
    keys = [
        "verbs", "verbs_rate", "nouns", "nouns_rate", "pronouns", "pronouns_rate",
        "adjectives", "adjectives_rate", "adverbs", "adverbs_rate", "interjections",
        "interjections_rate", "determiners", "determiners_rate", "conjunctions",
        "conjunctions_rate", "prepositions", "prepositions_rate", "auxiliary_verbs",
        "auxiliary_verbs_rate", "particles", "particles_rate", "numbers", "numbers_rate",
        "total_counts", "ocw", "ccw", "content_density", "open_class_words_rate",
        "lexical_diversity", "ttr", "brunets_index", "honore_statistic", "hypernym_count",
        "lexical_sophistication", "lexical_density", "function_word_count",
        "syntactic_complexity", "dependent_clauses_per_sentence", "passive_voice_count",
        "passive_voice_rate", "ref_r_real", "word_count", "sentence_count",
        "mean_sentence_length", "std_sentence_length", "syllables", "reading_time",
        "dale_chall", "flesch", "coleman_liau_index", "automated_readability_index",
        "gunning_fog", "polarity", "subjectivity", "disfluencies", "cohesion_score",
        "personal_deixis_rate", "spatial_deixis_rate", "temporal_deixis_rate",
        "past_tense_rate", "present_tense_rate", "future_tense_rate",
    ]
    return {k: 0.0 for k in keys}
