import importlib.util
from pathlib import Path

import pandas as pd

main_spec = importlib.util.spec_from_file_location("main", Path(__file__).resolve().parents[1] / "main.py")
main = importlib.util.module_from_spec(main_spec)
main_spec.loader.exec_module(main)


def test_processed_datasets_are_written_under_output_root(tmp_path, monkeypatch):
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

    processed_data = output_dir / "processed-data"
    assert (processed_data / "processed_features_all.csv").is_file()
    assert (processed_data / "processed_features_unique.csv").is_file()
