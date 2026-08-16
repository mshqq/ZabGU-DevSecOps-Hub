import os

import pytest

import app.scanner.clone as clone_module
from app.scanner.clone import cleanup, clone_repo
from app.scanner.exceptions import RepoCloneError, RepoTooLargeError
from app.utils import is_allowed_url


def test_clone_repo_real_github():
    path, sha = clone_repo(url="https://github.com/mshqq/mshqq.git")
    try:
        assert os.path.isdir(path)
        assert sha
        assert len(sha) == 40
    finally:
        cleanup(path)


def test_clone_repo_specific_commit():
    commit_sha = "bce38ad98aa578b9603d84ef74505c60ceb287ef"

    path, sha = clone_repo(
        url="https://github.com/mshqq/mshqq.git", commit_sha=commit_sha
    )
    try:
        assert os.path.isdir(path)
        assert sha == commit_sha
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
    assert is_allowed_url(url) is status


def test_cleanup_removes_directory(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "file.txt").write_text("data")

    cleanup(str(repo_dir))

    assert not os.path.isdir(repo_dir)


def test_cleanup_nonexistent_path_does_not_raise(tmp_path):
    missing_dir = tmp_path / "missing"

    cleanup(str(missing_dir))


def test_clone_repo_too_large():
    original_max = clone_module.MAX_REPO_SIZE_MB
    clone_module.MAX_REPO_SIZE_MB = 0

    try:
        with pytest.raises(RepoTooLargeError):
            clone_repo(url="https://github.com/mshqq/mshqq.git")
    finally:
        clone_module.MAX_REPO_SIZE_MB = original_max
