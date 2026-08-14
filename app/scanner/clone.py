import os
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse

from app.scanner.exceptions import RepoCloneError, RepoTooLargeError

SCAN_TEMP_DIR = ""

MAX_REPO_SIZE_MB = 500
GIT_TIMEOUT_SECONDS = 30

ALLOWED_HOSTS = ("github.com", "gitlab.com")


def _check_repo_size(path: str) -> int:
    total = 0

    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        for name in filenames:
            file_path = os.path.join(dirpath, name)
            if os.path.islink(file_path):
                continue
            try:
                total += os.path.getsize(file_path)
            except OSError:
                continue

    return total


def _run_git(args: list[str], cwd: str, timeout: int) -> None:
    try:
        subprocess.run(
            ["git", *args],
            check=True,
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        raise RepoCloneError(f"git {' '.join(args)} failed: {stderr or e}") from e
    except subprocess.TimeoutExpired as e:
        raise RepoCloneError(f"git {' '.join(args)} timed out after {timeout}s") from e


def _is_allowed_url(url: str) -> bool:
    if not url:
        return False

    parsed = urlparse(url)
    if parsed.scheme in ("http", "https"):
        host = parsed.hostname

        return host is not None and host.lower() in ALLOWED_HOSTS

    if url.startswith("git@"):
        rest = url[len("git@") :]
        host, sep, path = rest.partition(":")

        return bool(sep) and bool(host) and bool(path) and host.lower() in ALLOWED_HOSTS

    return False


def clone_repo(url: str, commit_sha: str | None = None) -> tuple[str, str]:
    if not _is_allowed_url(url):
        raise RepoCloneError("URL не разрешён (нужен http(s):// или git@host:...)")

    ref: str = commit_sha or "HEAD"
    temp_folder_path: str = tempfile.mkdtemp(dir=SCAN_TEMP_DIR or None, prefix="scan_")

    try:
        _run_git(["init"], temp_folder_path, GIT_TIMEOUT_SECONDS)
        _run_git(
            ["remote", "add", "origin", url], temp_folder_path, GIT_TIMEOUT_SECONDS
        )
        _run_git(
            ["fetch", "--depth=1", "origin", ref], temp_folder_path, GIT_TIMEOUT_SECONDS
        )
        _run_git(["checkout", "FETCH_HEAD"], temp_folder_path, GIT_TIMEOUT_SECONDS)

        resolved_sha = _get_head_sha(temp_folder_path)

        size_bytes = _check_repo_size(temp_folder_path)
        max_bytes = MAX_REPO_SIZE_MB * 1024 * 1024

        if size_bytes > max_bytes:
            raise RepoTooLargeError(
                f"Размер репозитория {size_bytes / (1024 * 1024):.1f}MB "
                f"превышает лимит {MAX_REPO_SIZE_MB}MB"
            )
    except (RepoCloneError, RepoTooLargeError):
        shutil.rmtree(temp_folder_path, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(temp_folder_path, ignore_errors=True)
        raise RepoCloneError(f"Не удалось клонировать {url}: {e}") from e

    return temp_folder_path, resolved_sha


def _get_head_sha(repo_path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            cwd=repo_path,
            timeout=GIT_TIMEOUT_SECONDS,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        raise RepoCloneError(f"Не удалось получить хэш коммита: {e}") from e

    return result.stdout.strip()


def cleanup(repo_path: str) -> None:
    shutil.rmtree(repo_path, ignore_errors=True)
