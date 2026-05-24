from dataclasses import asdict, dataclass
from typing import Literal


Severity = Literal["low", "medium", "high"]


@dataclass
class ValidationIssue:
    severity: Severity
    category: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
