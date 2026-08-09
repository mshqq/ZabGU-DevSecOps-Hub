import os
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ScanContext:
    repo_path: str
    commit_sha: str
    files: list[str]

    def abs_path(self, rel: str) -> str:
        return os.path.join(self.repo_path, rel)


class Rule(ABC):
    rule_id: str = ""
    severity: str = "P2"  # P0 | P1 | P2
    confidence: str = "medium"  # high | medium | low
    source: str = "regex"  # regex | filename

    @abstractmethod
    def scan(self, ctx: ScanContext) -> list[dict]: ...

    @staticmethod
    def mask_secret(value: str) -> str:
        if not value or len(value) < 12:
            return "****"
        return f"{value[:4]}****{value[-4:]}"

    def make_finding(
        self,
        *,
        file_path: str,
        line_no: int | None = None,
        secret: str,
        context: dict | None = None,
        commit_sha: str | None = None,
    ) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "confidence": self.confidence,
            "source": self.source,
            "file_path": file_path,
            "line_no": line_no,
            "commit_sha": commit_sha,
            "masked_value": self.mask_secret(secret),
            "context": context or {},
        }
