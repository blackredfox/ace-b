from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from aceb.eval.validation import MetricValidationSuiteResult, run_metric_validation_suite

if TYPE_CHECKING:
    from aceb.config import BenchmarkConfig


@dataclass
class EvidenceClaim:
    name: str
    supported: bool
    explanation: str
    evidence_keys: list[str]


@dataclass
class EvidenceSummary:
    metric_validation_passed: bool
    behavioral_separation_passed: bool
    claims: list[EvidenceClaim]
    metric_validation_details: dict[str, dict[str, object]]
    baseline_summary: dict[str, dict[str, float | None]]
    behavioral_separation_checks: dict[str, bool]


def build_evidence_summary(config: BenchmarkConfig) -> EvidenceSummary:
    from aceb.validation.run_validation import run_validation_with_summary, validate_behavioral_separation

    metric_validation = run_metric_validation_suite()
    validation_result = run_validation_with_summary(config)
    baseline_summary = validation_result["summary"]
    behavioral_checks = validate_behavioral_separation(baseline_summary)
    metric_validation_details = _build_metric_validation_details(metric_validation)

    return EvidenceSummary(
        metric_validation_passed=all(check.passed for check in metric_validation.checks),
        behavioral_separation_passed=all(behavioral_checks.values()),
        claims=_build_claims(metric_validation_details, behavioral_checks),
        metric_validation_details=metric_validation_details,
        baseline_summary=baseline_summary,
        behavioral_separation_checks=behavioral_checks,
    )


def render_evidence_summary_markdown(summary: EvidenceSummary) -> str:
    pcm_check = summary.metric_validation_details["pcm_construct_validity"]["passed"]
    cdl_check = summary.metric_validation_details["cdl_window_behavior"]["passed"]
    pr_check = summary.metric_validation_details["pr_perseveration_specificity"]["passed"]
    non_redundancy_check = summary.metric_validation_details["metric_non_redundancy"]["passed"]

    lines = [
        "# ACE-B / RCS-1 Evidence Summary",
        "",
        "## Metric Validity",
        f"- PCM: {_pass_fail(pcm_check)}",
        f"- CDL: {_pass_fail(cdl_check)}",
        f"- PR: {_pass_fail(pr_check)}",
        f"- Non-redundancy: {_pass_fail(non_redundancy_check)}",
        "",
        "## Baseline Separation",
        f"- Random vs Static PCM: {_pass_fail(summary.behavioral_separation_checks['random_vs_static_pcm'])}",
        f"- Adaptive vs Static CDL: {_pass_fail(summary.behavioral_separation_checks['adaptive_vs_static_cdl'])}",
        f"- Adaptive vs Static PR: {_pass_fail(summary.behavioral_separation_checks['adaptive_vs_static_pr'])}",
        "",
        "## Claims",
    ]

    for claim in summary.claims:
        lines.append(f"- {_pass_fail(claim.supported)} — {claim.explanation}")

    return "\n".join(lines)


def _build_metric_validation_details(
    metric_validation: MetricValidationSuiteResult,
) -> dict[str, dict[str, object]]:
    return {
        check.name: {
            "passed": check.passed,
            "details": check.details,
        }
        for check in metric_validation.checks
    }


def _build_claims(
    metric_validation_details: dict[str, dict[str, object]],
    behavioral_checks: dict[str, bool],
) -> list[EvidenceClaim]:
    return [
        EvidenceClaim(
            name="pcm_measures_pre_change_mastery",
            supported=bool(metric_validation_details["pcm_construct_validity"]["passed"]),
            explanation="PCM is supported as a mastery metric because stronger pre-switch correctness yields higher PCM.",
            evidence_keys=["metric_validation_details.pcm_construct_validity"],
        ),
        EvidenceClaim(
            name="cdl_measures_detection_lag_not_lucky_hits",
            supported=bool(metric_validation_details["cdl_window_behavior"]["passed"]),
            explanation="CDL is supported as a lag metric because isolated lucky correct steps do not trigger recovery.",
            evidence_keys=["metric_validation_details.cdl_window_behavior"],
        ),
        EvidenceClaim(
            name="pr_measures_perseveration_not_generic_error",
            supported=bool(metric_validation_details["pr_perseveration_specificity"]["passed"]),
            explanation="PR is supported as a perseveration metric because old-rule-consistent errors score higher than generic mistakes.",
            evidence_keys=["metric_validation_details.pr_perseveration_specificity"],
        ),
        EvidenceClaim(
            name="metrics_are_not_reducible_to_accuracy",
            supported=bool(metric_validation_details["metric_non_redundancy"]["passed"]),
            explanation="The metrics are supported as non-redundant because matched accuracy cases still separate on CDL or PR.",
            evidence_keys=["metric_validation_details.metric_non_redundancy"],
        ),
        EvidenceClaim(
            name="baseline_agents_show_behavioral_separation",
            supported=all(behavioral_checks.values()),
            explanation="Baseline agents show separation because random, static, and adaptive policies diverge on mastery and recovery checks.",
            evidence_keys=[
                "behavioral_separation_checks.random_vs_static_pcm",
                "behavioral_separation_checks.adaptive_vs_static_cdl",
                "behavioral_separation_checks.adaptive_vs_static_pr",
            ],
        ),
    ]


def _pass_fail(value: bool) -> str:
    return "PASS" if value else "FAIL"