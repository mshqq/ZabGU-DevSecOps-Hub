import os

import pytest

from app.scanner.clone import _is_allowed_url, cleanup, clone_repo
from app.scanner.exceptions import RepoCloneError


def test_clone_repo_real_github():
    path, sha = clone_repo(url="https://github.com/mshqq/mshqq.git")
    try:
        assert os.path.isdir(path)
        assert sha
        assert len(sha) == 40
    finally:
        cleanup(path)


def test_clone_nonexist_repo_raises():
    with pytest.raises(RepoCloneError):
        clone_repo(url="https://github.com/nonexist/nonexist-repo.git")


@pytest.mark.parametrize(
    "url, status",
    [
        ("https://github.com/owner/repo.git", True),
        ("http://github.com/owner/repo.git", True),
        ("https://gitlab.com/owner/repo.git", True),
        ("git@github.com:owner/repo.git", True),
        ("git@gitlab.com:owner/repo", True),
        ("file:///etc/passwd", False),
        ("local/path/to/repo", False),
        ("../relative/path", False),
        ("https://badurl.com/owner/repo", False),
        ("git@evil.com:owner/repo", False),
        ("git@github.com", False),
        ("", False),
        ("https://github.com.badurl.com", False),
        ("HTTPS://GITHUB.COM/owner/repo.git", True),
        ("git@github.com:", False),
    ],
)
def test_is_allowed_url(url, status):
    assert _is_allowed_url(url) is status


def test_cleanup_removes_directory(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "file.txt").write_text("data")

    cleanup(str(repo_dir))

    assert not os.path.isdir(repo_dir)


def test_cleanup_nonexistent_path_does_not_raise(tmp_path):
    missing_dir = tmp_path / "missing"

    cleanup(str(missing_dir))
