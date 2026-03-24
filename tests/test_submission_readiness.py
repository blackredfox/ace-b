from __future__ import annotations

from pathlib import Path

from aceb.config import BenchmarkConfig
from aceb.eval.evidence_summary import build_evidence_summary
from aceb.validation.run_validation import run_validation_with_summary


NARRATIVE_DIR = Path("/app/aceb/narrative")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_required_narrative_files_exist_and_are_non_empty() -> None:
    required = [
        NARRATIVE_DIR / "kaggle_writeup.md",
        NARRATIVE_DIR / "results_snapshot.md",
        NARRATIVE_DIR / "submission_checklist.md",
    ]
    for path in required:
        assert path.exists(), f"Missing required file: {path}"
        assert _read(path).strip(), f"File is empty: {path}"


def test_optional_support_files_are_present_and_have_expected_scope() -> None:
    dataset_notes = NARRATIVE_DIR / "dataset_notes.md"
    packaging_notes = NARRATIVE_DIR / "benchmark_packaging_notes.md"

    assert dataset_notes.exists()
    assert packaging_notes.exists()

    dataset_text = _read(dataset_notes)
    packaging_text = _read(packaging_notes)

    assert "# Dataset Notes" in dataset_text
    assert "# Benchmark Packaging Notes" in packaging_text
    assert "packaging readiness only" in packaging_text.lower()


def test_kaggle_writeup_required_section_order() -> None:
    text = _read(NARRATIVE_DIR / "kaggle_writeup.md")
    required_headers = [
        "# Project Name",
        "# Your Team",
        "# Problem Statement",
        "# Task & benchmark construction",
        "# Dataset",
        "# Technical details",
        "# Results, insights, and conclusions",
        "# Organizational affiliations",
        "# References & citations",
    ]

    positions = [text.find(header) for header in required_headers]
    assert all(position != -1 for position in positions)
    assert positions == sorted(positions)


def test_kaggle_writeup_explicitly_mentions_track_and_competition_aligned_references() -> None:
    text = _read(NARRATIVE_DIR / "kaggle_writeup.md")

    assert "Executive Functions" in text
    assert "cognitive flexibility, rule switching, and resistance to perseverative errors" in text
    assert "Measuring Progress Toward AGI: Cognitive Abilities" in text
    assert "Measuring Progress Toward AGI: A Cognitive Framework" in text


def test_results_snapshot_matches_current_validation_baseline_summary() -> None:
    config = BenchmarkConfig(alphabet_size=6, input_length=20, history_window=4, seed=24680)
    summary = run_validation_with_summary(config)["summary"]
    text = _read(NARRATIVE_DIR / "results_snapshot.md")

    expected_rows = [
        (
            "RandomAgent",
            f"{summary['RandomAgent']['accuracy']:.2f}",
            f"{summary['RandomAgent']['pcm']:.3f}",
            f"{summary['RandomAgent']['cdl']:.1f}" if summary["RandomAgent"]["cdl"] is not None else "None",
            f"{summary['RandomAgent']['pr']:.3f}",
        ),
        (
            "StaticShiftAgent",
            f"{summary['StaticShiftAgent']['accuracy']:.2f}",
            f"{summary['StaticShiftAgent']['pcm']:.3f}",
            f"{summary['StaticShiftAgent']['cdl']:.1f}" if summary["StaticShiftAgent"]["cdl"] is not None else "None",
            f"{summary['StaticShiftAgent']['pr']:.2f}",
        ),
        (
            "AdaptiveShiftAgent",
            f"{summary['AdaptiveShiftAgent']['accuracy']:.2f}",
            f"{summary['AdaptiveShiftAgent']['pcm']:.3f}",
            f"{summary['AdaptiveShiftAgent']['cdl']:.1f}" if summary["AdaptiveShiftAgent"]["cdl"] is not None else "None",
            f"{summary['AdaptiveShiftAgent']['pr']:.2f}",
        ),
    ]

    for agent, accuracy, pcm, cdl, pr in expected_rows:
        assert f"| {agent} | {accuracy} | {pcm} | {cdl} | {pr} |" in text

    assert "same strong `PCM`" in text
    assert "differ sharply in `CDL` and `PR`" in text
    assert "Plain accuracy is insufficient" in text


def test_dataset_notes_cover_required_episode_spec_and_dataset_properties() -> None:
    text = _read(NARRATIVE_DIR / "dataset_notes.md")
    required_fields = {
        "episode_id",
        "alphabet",
        "input_stream",
        "shift_pre",
        "shift_post",
        "switch_step",
        "history_window",
        "seed",
    }
    for field in required_fields:
        assert f"`{field}`" in text

    lower = text.lower()
    assert "procedural" in lower
    assert "verifiable" in lower
    assert "ground truth is verifiable and ambiguity is minimized by construction" in lower


def test_submission_checklist_contains_required_items_and_privacy_note() -> None:
    text = _read(NARRATIVE_DIR / "submission_checklist.md")
    required_items = [
        "Kaggle Writeup completed",
        "Track selected",
        "Benchmark created in Kaggle Benchmarks",
        "Underlying tasks created and linked",
        "Benchmark attached as project link",
        "Cover image prepared",
        "Results section added",
        "Organizational affiliations section added",
        "References & citations added",
        "Final word count checked (<1500)",
        "Final Writeup submitted before deadline",
    ]
    for item in required_items:
        assert item in text

    assert "private kaggle resources attached to a public writeup will become public after the deadline" in text.lower()


def test_benchmark_packaging_notes_cover_input_output_verification_and_grouping() -> None:
    text = _read(NARRATIVE_DIR / "benchmark_packaging_notes.md").lower()
    assert "task input" in text
    assert "expected output" in text
    assert "verification logic" in text
    assert "benchmark grouping" in text


def test_evidence_summary_lazy_import_path_works_end_to_end() -> None:
    config = BenchmarkConfig(alphabet_size=6, input_length=20, history_window=4, seed=24680)
    summary = build_evidence_summary(config)

    assert summary.metric_validation_details
    assert set(summary.baseline_summary.keys()) == {"RandomAgent", "StaticShiftAgent", "AdaptiveShiftAgent"}