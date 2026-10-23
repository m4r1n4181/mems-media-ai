"""Settings from environment variables (with sensible local defaults).

Secrets such as API keys go in ``ml-service/.env`` (git-ignored), one ``NAME=value`` per line.
Real environment variables win over the file.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = (part.strip() for part in line.split("=", 1))
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]          # NAME="value" or NAME='value'
        os.environ.setdefault(name, value)


load_env_file()


@dataclass
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("ML_DATA_DIR",
                                                                       Path(__file__).resolve().parents[1] / "data")))
    # LLM used to draft outreach e-mails: ollama | openai | anthropic | template
    llm_provider: str = field(default_factory=lambda: os.environ.get("LLM_PROVIDER", "ollama").lower())
    ollama_url: str = field(default_factory=lambda: os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    ollama_model: str | None = field(default_factory=lambda: os.environ.get("OLLAMA_MODEL"))
    openai_url: str = field(default_factory=lambda: os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_model: str | None = field(default_factory=lambda: os.environ.get("OPENAI_MODEL"))
    openai_key: str | None = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    # Extra provider-specific fields merged into the request, e.g. {"enable_thinking": false} for Qwen
    openai_extra_body: dict = field(default_factory=lambda: json.loads(os.environ.get("OPENAI_EXTRA_BODY") or "{}"))
    anthropic_model: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_MODEL", "claude-haiku-5-5"))
    anthropic_key: str | None = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY"))
    llm_timeout_s: float = field(default_factory=lambda: float(os.environ.get("LLM_TIMEOUT_S", "120")))


settings = Settings()
