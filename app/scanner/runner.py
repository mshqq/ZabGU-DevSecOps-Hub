from dataclasses import dataclass

from app.scanner.base import Rule, ScanContext
from app.scanner.rules import ALL_RULES

MAX_FINDINGS_PER_SCAN = 10


@dataclass(frozen=True)
class ScanResult:
    findings: list[dict]
    truncated: bool
    errors: list[Exception]


def run_rules(ctx: ScanContext, rules: list[Rule] | None = None) -> ScanResult:
    rules = ALL_RULES if rules is None else rules

    findings: list[dict[str, str]] = []
    errors: list[Exception] = []
    truncated = False

    for rule in rules:
        try:
            findings.extend(rule.scan(ctx))
        except Exception as e:  # noqa: BLE001
            errors.append(e)
            continue

    if len(findings) > MAX_FINDINGS_PER_SCAN:
        findings = findings[:MAX_FINDINGS_PER_SCAN]
        truncated = True

    return ScanResult(findings, truncated, errors)
