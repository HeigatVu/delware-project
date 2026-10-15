[Book index](README.md)

# Study and corpus

This repository implements the analysis in Nyongesa et al. (2025), *Artificial intelligence-driven natural language processing for identifying linguistic patterns in Alzheimer's disease and mild cognitive impairment*. The paper and extracted text are in [docs/paper](../docs/paper/).

## Research question

Can linguistic features from picture-description speech measure differences between Control and MCI groups, reveal groups of related features, and classify diagnosis?

## Corpus

The DementiaBank [Delaware corpus](https://dementia.talkbank.org/) contains TalkBank CHAT transcripts (`.cha`) for three picture tasks. The demographics workbook, `demo-test-fixed.xlsx`, provides age, sex, education, MoCA, and diagnosis.

| Task | Name used here |
|------|----------------|
| Cookie Theft | `Cookie` |
| Cat Rescue | `Cat` |
| Coming & Going (Rockwell) | `Rockwell` |

## Analysis

1. Parse participant speech and task labels from each transcript.
2. Match workbook demographics to transcript records by participant ID.
3. Extract 53 linguistic measures, returned as 63 columns, for each task record.
4. Compare diagnostic groups, adjust comparisons for age and education, and correlate features with MoCA.
5. Cluster feature correlations and classify diagnosis with cross-validated models.
6. Plot group differences, feature clusters, task profiles, and MoCA relationships.

> **Read cluster labels cautiously.** Domain names use a keyword heuristic. Inspect the feature members before interpreting a label; see the [module map](../src/delware_speech/README.md).

## Outputs

| Directory | Contents |
|-----------|----------|
| [Speech features](../output/README.md#speech-features) | Processed speech data, group comparisons, clustering, classification, and task profiles |
| [Cognitive scores](../output/README.md#cognitive-scores) | Feature correlations and plots against MoCA |

The original Python and R scripts are preserved in `reference_repo/speech/` for comparison.

[Next: Architecture](architecture.md) · [Quickstart](quickstart.md)
