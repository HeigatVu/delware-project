import importlib.util
from pathlib import Path

import pandas as pd

main_spec = importlib.util.spec_from_file_location("main", Path(__file__).resolve().parents[1] / "main.py")
main = importlib.util.module_from_spec(main_spec)
main_spec.loader.exec_module(main)


def test_output_paths_follow_source_domains_and_keep_overrides(tmp_path, monkeypatch):
    source = pd.DataFrame(
        {
            "ID": ["p1-1", "p2-1"],
            "Record_ID": ["p1", "p2"],
            "Task": ["Cookie Theft", "Cookie Theft"],
            "Diagnosis": ["Control", "MCI"],
            "Age": [65, 70],
            "Education_Years": [12, 16],
            "MoCA": [25, 20],
            "token_count": [20, 24],
        }
    )
    monkeypatch.setattr(main, "process_dataset", lambda *_args, **_kwargs: source.copy())
    monkeypatch.setattr(pd.DataFrame, "to_excel", lambda *_args, **_kwargs: None)

    output_dir = tmp_path / "output"
    main.run_pipeline(
        corpus_root="unused",
        demo_excel="unused",
        output_dir=str(output_dir),
        do_stats=False,
        do_cluster=False,
        do_importance=False,
        do_visualize=False,
    )

    speech_features = output_dir / "speech-features"
    processed_data = speech_features / "processed-data"
    assert (processed_data / "processed_features_all.csv").is_file()
    assert (processed_data / "processed_features_unique.csv").is_file()
    assert (speech_features / "group-comparisons").is_dir()
    assert (output_dir / "cognitive-scores").is_dir()

    data_dir = tmp_path / "custom-data"
    results_dir = tmp_path / "custom-results"
    figures_dir = tmp_path / "custom-figures"
    main.run_pipeline(
        corpus_root="unused",
        demo_excel="unused",
        output_dir=str(output_dir),
        data_dir=str(data_dir),
        results_dir=str(results_dir),
        figures_dir=str(figures_dir),
        do_stats=False,
        do_cluster=False,
        do_importance=False,
        do_visualize=False,
    )

    assert (data_dir / "processed_features_all.csv").is_file()
    assert (results_dir / "cognitive-scores").is_dir()
    assert (figures_dir / "cognitive-scores").is_dir()
