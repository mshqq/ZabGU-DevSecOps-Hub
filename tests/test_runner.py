import pytest

from app.scanner.base import Rule, ScanContext
from app.scanner.runner import MAX_FINDINGS_PER_SCAN, ScanResult, run_rules
from tests.utils import get_test_folder_path


class OkRule(Rule):
    rule_id = "OK_RULE"
    severity = "P2"
    confidence = "medium"
    source = "regex"

    def scan(self, ctx):
        return [
            self.make_finding(
                file_path="config.py",
                line_no=1,
                secret="AFOKEOFKOEKF",
                commit_sha=ctx.commit_sha,
            )
        ]


class AlmostOkRule(Rule):
    rule_id = "ALSO_OK_RULE"
    severity = "P1"
    confidence = "high"
    source = "filename"

    def __init__(self, count):
        self.count = count

    def scan(self, ctx):
        return [
            self.make_finding(
                file_path="config.py",
                line_no=4,
                secret="OKGPKSPO",
                commit_sha=ctx.commit_sha,
            )
            for _ in range(self.count)
        ]


class BrokenRule(Rule):
    rule_id = "BROKEN_RULE"
    severity = "P0"
    confidence = "low"
    source = "filename"

    def scan(self, ctx):
        raise RuntimeError("Ошибка в правиле BrokenRule")


@pytest.fixture
def ctx():
    return ScanContext(str(get_test_folder_path()), "abcdefgh", ["config.py", ".env"])


def test_run_rules_normal(ctx):
    result: ScanResult = run_rules(ctx, rules=[OkRule()])

    assert len(result.findings) == 1
    assert result.truncated is False
    assert result.errors == []


def test_run_default_rules(ctx):
    result: ScanResult = run_rules(ctx)

    assert any(f["rule_id"] == "ENV_FILE_COMMITED" for f in result.findings)


def test_broken_rule_not_stop_others(ctx):
    result: ScanResult = run_rules(
        ctx, rules=[OkRule(), BrokenRule(), AlmostOkRule(count=1)]
    )

    assert len(result.findings) == 2
    assert result.truncated is False
    assert len(result.errors) == 1
    assert isinstance(result.errors[0], RuntimeError)
    assert str(result.errors[0]) == "Ошибка в правиле BrokenRule"


def test_max_findings_per_scan(ctx):
    result: ScanResult = run_rules(
        ctx, rules=[AlmostOkRule(count=MAX_FINDINGS_PER_SCAN + 5)]
    )

    assert len(result.findings) == MAX_FINDINGS_PER_SCAN
    assert result.truncated is True


def test_max_findings_edge_case(ctx):
    result: ScanResult = run_rules(
        ctx, rules=[AlmostOkRule(count=MAX_FINDINGS_PER_SCAN)]
    )

    assert len(result.findings) == MAX_FINDINGS_PER_SCAN
    assert result.truncated is False
