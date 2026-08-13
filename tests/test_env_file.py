from pathlib import Path

import pytest

from app.scanner.base import ScanContext
from app.scanner.rules.env_file import (
    EnvFileRule,
    _basename,
    _is_env_filename,
    _strip_quotes,
)

here: Path = Path(__file__).resolve().parent
test_repo_folder: Path = here / "test-repo"


@pytest.mark.parametrize(
    "filename, correct_status",
    [
        (".env.example", False),
        (".env.sample", False),
        (".env.template", False),
        ("config.py", False),
        (".env", True),
        (".env.local", True),
        (".env.production", True),
        (".environment", False),
        (".ENV", False),
        ("app/.env", False),
    ],
)
def test_is_env_filename(filename, correct_status):
    assert _is_env_filename(filename) is correct_status


@pytest.mark.parametrize(
    "filename, correct_name",
    [
        ("app/.env", ".env"),
        ("", ""),
        (".env", ".env"),
        ("app/models/.env", ".env"),
        ("/app/.env", ".env"),
        ("app/models/", ""),
    ],
)
def test_basename(filename, correct_name):
    assert _basename(filename) == correct_name


@pytest.mark.parametrize(
    "value, correct_value",
    [
        ('"admin"', "admin"),
        ("'p@ssw0rd123456'", "p@ssw0rd123456"),
        ("novalue", "novalue"),
        ("", ""),
        ('"', '"'),
        ("'", "'"),
        ('""', ""),
        ("''", ""),
        ('"admin', '"admin'),
        ("'admin\"", "'admin\""),
    ],
)
def test_strip_quotes(value, correct_value):
    assert _strip_quotes(value) == correct_value


def _run_scan():
    sc = ScanContext(
        str(test_repo_folder),
        "abcd",
        [
            ".env",
            ".env.example",
            ".env.sample",
            ".env.template",
            "config.py",
            ".env.local",
            ".env.production",
            ".env.comments",
            ".env.huge",
            ".env.binary",
        ],
    )
    return EnvFileRule().scan(sc)


def test_env_file_rule():
    findings = _run_scan()

    assert len(findings) == 8

    for f in findings:
        assert f["rule_id"] == "ENV_FILE_COMMITED"
        assert f["severity"] == "P0"
        assert f["confidence"] == "high"
        assert f["source"] == "regex"
        assert f["commit_sha"] == "abcd"
        assert f["line_no"] is not None
        assert "key" in f["context"]


def test_env_file_rule_only_reports_env_files():
    findings = _run_scan()
    reported_files = {f["file_path"] for f in findings}

    assert ".env.example" not in reported_files
    assert ".env.sample" not in reported_files
    assert ".env.template" not in reported_files
    assert "config.py" not in reported_files


def test_env_file_rule_reports_real_env_files():
    findings = _run_scan()
    reported_files = {f["file_path"] for f in findings}

    assert ".env" in reported_files
    assert ".env.local" in reported_files
    assert ".env.production" in reported_files


def test_env_file_rule_skips_huge_file():
    findings = _run_scan()
    reported_files = {f["file_path"] for f in findings}

    assert ".env.huge" not in reported_files


def test_env_file_rule_skips_binary_file():
    findings = _run_scan()
    reported_files = {f["file_path"] for f in findings}

    assert ".env.binary" not in reported_files


def test_env_file_rule_no_empty_values():
    findings = _run_scan()
    for f in findings:
        assert f["masked_value"] != ""
