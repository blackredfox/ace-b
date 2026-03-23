import unittest

from aceb.config import BenchmarkConfig
from aceb.eval.evidence_summary import (
    EvidenceSummary,
    build_evidence_summary,
    render_evidence_summary_markdown,
)
from aceb.eval.validation import run_metric_validation_suite
from aceb.validation.run_validation import run_validation_with_summary, validate_behavioral_separation


class EvidenceSummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BenchmarkConfig(
            alphabet_size=6,
            input_length=20,
            history_window=4,
            seed=24680,
        )

    def test_build_evidence_summary_returns_valid_structure(self) -> None:
        summary = build_evidence_summary(self.config)

        self.assertIsInstance(summary, EvidenceSummary)

    def test_expected_claim_names_are_present(self) -> None:
        summary = build_evidence_summary(self.config)

        self.assertEqual(
            {claim.name for claim in summary.claims},
            {
                "pcm_measures_pre_change_mastery",
                "cdl_measures_detection_lag_not_lucky_hits",
                "pr_measures_perseveration_not_generic_error",
                "metrics_are_not_reducible_to_accuracy",
                "baseline_agents_show_behavioral_separation",
            },
        )

    def test_summary_includes_metric_validation_baseline_summary_and_behavior_checks(self) -> None:
        summary = build_evidence_summary(self.config)

        self.assertIn("pcm_construct_validity", summary.metric_validation_details)
        self.assertEqual(set(summary.baseline_summary.keys()), {"RandomAgent", "StaticShiftAgent", "AdaptiveShiftAgent"})
        self.assertEqual(
            set(summary.behavioral_separation_checks.keys()),
            {"random_vs_static_pcm", "adaptive_vs_static_cdl", "adaptive_vs_static_pr"},
        )

    def test_metric_validation_passed_reflects_validation_suite(self) -> None:
        summary = build_evidence_summary(self.config)
        suite = run_metric_validation_suite()

        self.assertEqual(summary.metric_validation_passed, all(check.passed for check in suite.checks))

    def test_behavioral_separation_passed_reflects_sanity_checks(self) -> None:
        summary = build_evidence_summary(self.config)
        behavioral_checks = validate_behavioral_separation(run_validation_with_summary(self.config)["summary"])

        self.assertEqual(summary.behavioral_separation_passed, all(behavioral_checks.values()))

    def test_claims_include_metric_validation_and_behavioral_separation_evidence_links(self) -> None:
        summary = build_evidence_summary(self.config)

        self.assertTrue(any(key.startswith("metric_validation_details.") for claim in summary.claims for key in claim.evidence_keys))
        self.assertTrue(any(key.startswith("behavioral_separation_checks.") for claim in summary.claims for key in claim.evidence_keys))

    def test_markdown_output_is_deterministic(self) -> None:
        first = render_evidence_summary_markdown(build_evidence_summary(self.config))
        second = render_evidence_summary_markdown(build_evidence_summary(self.config))

        self.assertEqual(first, second)

    def test_markdown_output_includes_key_sections(self) -> None:
        markdown = render_evidence_summary_markdown(build_evidence_summary(self.config))

        self.assertIn("## Metric Validity", markdown)
        self.assertIn("## Baseline Separation", markdown)
        self.assertIn("## Claims", markdown)


if __name__ == "__main__":
    unittest.main()