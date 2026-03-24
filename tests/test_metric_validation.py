import unittest
from unittest.mock import patch

from aceb.eval.core_metrics import evaluate_core_metrics
from aceb.eval.validation import (
    MetricValidationCheck,
    MetricValidationSuiteResult,
    run_metric_validation_suite,
    validate_cdl_window_behavior,
    validate_metric_non_redundancy,
    validate_pcm_construct,
    validate_pr_perseveration_specificity,
)


class MetricValidationSuiteTests(unittest.TestCase):
    def test_run_metric_validation_suite_returns_structured_result(self) -> None:
        result = run_metric_validation_suite()

        self.assertIsInstance(result, MetricValidationSuiteResult)
        self.assertTrue(all(isinstance(check, MetricValidationCheck) for check in result.checks))

    def test_all_required_validation_checks_are_present(self) -> None:
        result = run_metric_validation_suite()

        self.assertEqual(
            {check.name for check in result.checks},
            {
                "pcm_construct_validity",
                "cdl_window_behavior",
                "pr_perseveration_specificity",
                "metric_non_redundancy",
            },
        )

    def test_pcm_construct_check_passes(self) -> None:
        self.assertTrue(validate_pcm_construct().passed)

    def test_cdl_window_behavior_check_passes(self) -> None:
        self.assertTrue(validate_cdl_window_behavior().passed)

    def test_pr_perseveration_specificity_check_passes(self) -> None:
        self.assertTrue(validate_pr_perseveration_specificity().passed)

    def test_metric_non_redundancy_check_passes(self) -> None:
        self.assertTrue(validate_metric_non_redundancy().passed)

    def test_pr_differs_while_accuracy_is_the_same(self) -> None:
        details = validate_metric_non_redundancy().details
        case_1 = details["case_same_accuracy_perseverative"]
        case_2 = details["case_same_accuracy_non_perseverative"]

        self.assertEqual(case_1["accuracy"], case_2["accuracy"])
        self.assertGreater(case_1["pr"], case_2["pr"])

    def test_pcm_can_match_while_cdl_differs(self) -> None:
        details = validate_metric_non_redundancy().details
        case_1 = details["case_same_pcm_slow_recovery"]
        case_2 = details["case_same_pcm_recovery"]

        self.assertEqual(case_1["pcm"], case_2["pcm"])
        self.assertNotEqual(case_1["cdl"], case_2["cdl"])

    def test_validation_helpers_reuse_existing_evaluator_functions(self) -> None:
        with patch("aceb.eval.validation.evaluate_core_metrics", wraps=evaluate_core_metrics) as wrapped_evaluator:
            run_metric_validation_suite()

        self.assertGreater(wrapped_evaluator.call_count, 0)

    def test_repeated_validation_runs_are_deterministic(self) -> None:
        first = run_metric_validation_suite()
        second = run_metric_validation_suite()

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()