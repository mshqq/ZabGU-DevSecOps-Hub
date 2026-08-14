import os

from app.scanner.base import Rule, ScanContext

SAFE_ENV_FILES: tuple[str] = (".env.example", ".env.sample", ".env.template")

MAX_ENV_FILE_SIZE: int = 200 * 1024


def _is_env_filename(name: str) -> bool:
    if name != ".env" and not name.startswith(".env."):
        return False

    return not any(name.endswith(safe_name) for safe_name in SAFE_ENV_FILES)


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]

    return value


class EnvFileRule(Rule):
    rule_id = "ENV_FILE_COMMITED"
    severity = "P0"
    confidence = "high"
    source = "regex"

    def scan(self, ctx: ScanContext) -> list[dict]:
        findings: list = []

        for rel_path in ctx.files:
            file_name = _basename(rel_path)
            if not _is_env_filename(file_name):
                continue

            abs_path: str = ctx.abs_path(rel_path)

            try:
                if os.path.getsize(abs_path) > MAX_ENV_FILE_SIZE:
                    continue
                with open(abs_path, "r", encoding="UTF-8") as f:
                    text = f.read()
            except (OSError, UnicodeDecodeError):
                continue

            findings.extend(self._scan_lines(rel_path, text, ctx.commit_sha))

        return findings

    def _scan_lines(self, file_path: str, text: str, commit_sha: str) -> list[dict]:
        findings: list[dict] = []

        for line_no, raw_line in enumerate(text.splitlines(), start=1):
            line: str = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            try:
                key, value = line.split("=", 1)
            except ValueError:
                continue

            key: str = key.strip()
            value: str = _strip_quotes(value.strip())

            if not value:
                continue

            findings.append(
                self.make_finding(
                    file_path=file_path,
                    line_no=line_no,
                    secret=value,
                    context={"key": key},
                    commit_sha=commit_sha,
                )
            )

        return findings
