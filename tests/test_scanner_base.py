import json
from dataclasses import FrozenInstanceError

import pytest

from app.models.finding import Finding
from app.scanner.base import Rule, ScanContext


def test_mask_long_value():
    assert Rule.mask_secret("AKIATRHJKRIEOWP") == "AKIA****EOWP"


def test_mask_short_value():
    assert Rule.mask_secret("shortkey") == "****"


def test_mask_empty_value():
    assert Rule.mask_secret("") == "****"


def test_mask_secret_no_leak():
    secret = "AKIATRHJKRIEOWP"
    assert secret not in Rule.mask_secret(secret)


def test_mask_edge_case():
    secret = "12345678ABCD"
    assert Rule.mask_secret(secret) == "1234****ABCD"


def test_scan_context_attributes():
    sc = ScanContext("/tmp/repo/", "abcd", [".env", "config.py"])
    assert sc.repo_path == "/tmp/repo/"
    assert sc.commit_sha == "abcd"
    assert sc.files == [".env", "config.py"]


def test_scan_context_frozen():
    sc = ScanContext("/tmp/repo/", "abcd", [".env", "config.py"])
    with pytest.raises(FrozenInstanceError):
        sc.commit_sha = "other"


def test_scan_context_abs_path():
    sc = ScanContext("/tmp/repo/", "abcd", [".env", "config.py"])
    assert sc.abs_path("config/settings.py") == "/tmp/repo/config/settings.py"


def test_rule_direct_instance():
    with pytest.raises(TypeError):
        # pyrefly: ignore [bad-instantiation]
        Rule()


def test_rule_fake():
    class FakeRule(Rule):
        rule_id = "FAKE_KEY"
        severity = "P0"
        confidence = "high"
        source = "regex"

        def scan(self, ctx):
            raw_secret = "AKIAIOSFODNN7WXYZ"
            return [
                self.make_finding(
                    file_path="config/settings.py",
                    line_no=42,
                    secret=raw_secret,
                    commit_sha=ctx.commit_sha,
                )
            ]

    ctx = ScanContext("tmp/repo", "deadbeef", ["config/settings.py"])
    findings = FakeRule().scan(ctx)
    assert len(findings) == 1
    finding = findings[0]
    assert finding["rule_id"] == "FAKE_KEY"
    assert finding["severity"] == "P0"
    assert finding["confidence"] == "high"
    assert finding["source"] == "regex"
    assert finding["commit_sha"] == "deadbeef"
    assert finding["masked_value"] == "AKIA****WXYZ"
    assert "AKIAIOSFODNN7WXYZ" not in json.dumps(finding)


def test_rule_fake_matches_finding_model():
    class FakeRule(Rule):
        rule_id = "FAKE_KEY"
        severity = "P0"
        confidence = "high"
        source = "regex"

        def scan(self, ctx):
            raw_secret = "AKIAIOSFODNN7WXYZ"
            return [
                self.make_finding(
                    file_path="config/settings.py",
                    line_no=42,
                    secret=raw_secret,
                    commit_sha=ctx.commit_sha,
                )
            ]

    ctx = ScanContext("tmp/repo", "deadbeef", ["config/settings.py"])
    finding = FakeRule().scan(ctx)[0]

    expected_keys = {c.name for c in Finding.__table__.columns} - {
        "id",
        "scan_id",
        "status",
    }
    assert set(finding.keys()) == expected_keys
