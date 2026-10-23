"""Thin clients for the LLMs that can draft outreach e-mails. All return plain text from the model.

ollama     local models (default), http://localhost:11434
openai     any OpenAI-compatible chat API (OpenAI, LM Studio, vLLM, ...), needs OPENAI_MODEL
anthropic  Claude via the Messages API, needs ANTHROPIC_API_KEY
template   no model at all (deterministic fallback)
"""
from __future__ import annotations

import httpx

from .config import Settings


class LLMUnavailable(Exception):
    """The provider cannot be reached or is not configured; callers fall back to the template."""


PREFERRED = ("qwen", "llama", "mistral", "gemma", "phi")


class OllamaClient:
    name = "ollama"

    def __init__(self, s: Settings):
        self.url, self.model, self.timeout = s.ollama_url.rstrip("/"), s.ollama_model, s.llm_timeout_s

    def resolve_model(self) -> str:
        """Use OLLAMA_MODEL, or pick an installed chat model so the service works out of the box."""
        if self.model:
            return self.model
        try:
            tags = httpx.get(f"{self.url}/api/tags", timeout=5).json().get("models", [])
        except Exception as e:  # noqa: BLE001
            raise LLMUnavailable(f"Ollama not reachable at {self.url}: {e}") from e
        names = [t["name"] for t in tags if "embed" not in t["name"]]
        if not names:
            raise LLMUnavailable("Ollama has no models installed (try: ollama pull qwen2.5:7b)")
        names.sort(key=lambda n: next((i for i, p in enumerate(PREFERRED) if p in n), len(PREFERRED)))
        self.model = names[0]
        return self.model

    def chat(self, system: str, user: str) -> str:
        model = self.resolve_model()
        try:
            r = httpx.post(f"{self.url}/api/chat", timeout=self.timeout, json={
                "model": model, "stream": False, "format": "json", "options": {"temperature": 0.4},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
            r.raise_for_status()
            return r.json()["message"]["content"]
        except httpx.HTTPError as e:
            raise LLMUnavailable(f"Ollama request failed: {e}") from e


class OpenAIClient:
    name = "openai"

    def __init__(self, s: Settings):
        self.url, self.model, self.key, self.timeout = s.openai_url.rstrip("/"), s.openai_model, s.openai_key, s.llm_timeout_s
        self.extra_body = s.openai_extra_body

    def chat(self, system: str, user: str) -> str:
        if not self.model:
            raise LLMUnavailable("OPENAI_MODEL is not set")
        headers = {"Authorization": f"Bearer {self.key}"} if self.key else {}
        try:
            r = httpx.post(f"{self.url}/chat/completions", headers=headers, timeout=self.timeout, json={
                "model": self.model, "temperature": 0.4, "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                **self.extra_body})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise LLMUnavailable(f"OpenAI-compatible request failed: {e}") from e


class AnthropicClient:
    name = "anthropic"

    def __init__(self, s: Settings):
        self.model, self.key, self.timeout = s.anthropic_model, s.anthropic_key, s.llm_timeout_s

    def chat(self, system: str, user: str) -> str:
        if not self.key:
            raise LLMUnavailable("ANTHROPIC_API_KEY is not set")
        try:
            r = httpx.post("https://api.anthropic.com/v1/messages", timeout=self.timeout,
                           headers={"x-api-key": self.key, "anthropic-version": "2023-06-01"},
                           json={"model": self.model, "max_tokens": 800, "temperature": 0.4, "system": system,
                                 "messages": [{"role": "user", "content": user}]})
            r.raise_for_status()
            return "".join(b.get("text", "") for b in r.json()["content"])
        except httpx.HTTPError as e:
            raise LLMUnavailable(f"Anthropic request failed: {e}") from e


def make_client(s: Settings):
    return {"ollama": OllamaClient, "openai": OpenAIClient, "anthropic": AnthropicClient}.get(s.llm_provider,
                                                                                           lambda _: None)(s)
