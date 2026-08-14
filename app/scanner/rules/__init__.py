from app.scanner.base import Rule
from app.scanner.rules.env_file import EnvFileRule

ALL_RULES: list[Rule] = [EnvFileRule()]
