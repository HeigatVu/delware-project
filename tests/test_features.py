"""Tests for features extraction module."""

from delware_speech.features import (
    extract_linguistic_features,
    calculate_lexical_richness,
    count_disfluencies,
    _empty_feature_dict,
)

SAMPLE_TEXT = (
    "The boy is taking a cookie from the cookie jar. "
    "His sister is reaching up to help him. "
    "The mother is washing dishes at the overflowing sink, and uh, she is not paying attention."
)


def test_extract_linguistic_features_non_empty():
    feats = extract_linguistic_features(SAMPLE_TEXT)
    assert isinstance(feats, dict)
    assert len(feats) >= 53

    # Check key categories
    assert feats["word_count"] > 20
    assert feats["sentence_count"] == 3
    assert feats["nouns"] > 0
    assert feats["verbs"] > 0
    assert feats["pronouns"] > 0
    assert feats["adjectives"] >= 0
    assert feats["syntactic_complexity"] > 0
    assert feats["lexical_diversity"] > 0
    assert feats["ttr"] > 0
    assert feats["disfluencies"] >= 1  # 'uh' is in text
    assert feats["personal_deixis_rate"] > 0
    assert feats["spatial_deixis_rate"] >= 0
    assert feats["past_tense_rate"] >= 0
    assert feats["present_tense_rate"] > 0


def test_extract_linguistic_features_empty():
    feats = extract_linguistic_features("")
    assert isinstance(feats, dict)
    assert feats["word_count"] == 0.0
    assert feats["nouns"] == 0.0
    assert feats["verbs"] == 0.0

    empty_dict = _empty_feature_dict()
    assert set(feats.keys()) == set(empty_dict.keys())


def test_calculate_lexical_richness():
    tokens = ["the", "dog", "barked", "at", "the", "cat", "and", "the", "cat", "ran"]
    ttr, brunets, honore = calculate_lexical_richness(tokens)
    assert 0 < ttr <= 1.0
    assert brunets > 0
    assert honore >= 0


def test_count_disfluencies():
    text = "Well, uh, I think you know, um, it was like really hard."
    count = count_disfluencies(text)
    assert count >= 4
