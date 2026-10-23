import json

import httpx

from app import config, llm


def test_env_file_is_loaded_and_real_env_wins(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('# comment\nOPENAI_MODEL="qwen-test"\nOPENAI_API_KEY=from-file\n'
                   'OPENAI_EXTRA_BODY={"enable_thinking": false}\n', encoding="utf-8")
    for name in ("OPENAI_MODEL", "OPENAI_EXTRA_BODY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "from-shell")

    config.load_env_file(env)
    s = config.Settings()

    assert s.openai_model == "qwen-test"
    assert s.openai_key == "from-shell"
    assert s.openai_extra_body == {"enable_thinking": False}


def test_openai_client_sends_extra_body(monkeypatch):
    sent = {}

    def fake_post(url, headers, timeout, json):
        sent.update(url=url, headers=headers, body=json)
        return httpx.Response(200, request=httpx.Request("POST", url),
                              json={"choices": [{"message": {"content": '{"subject": "s", "body": "b"}'}}]})

    monkeypatch.setattr(llm.httpx, "post", fake_post)
    s = config.Settings(openai_url="https://example.test/v1/", openai_model="qwen-test", openai_key="k",
                        openai_extra_body={"enable_thinking": False})

    out = llm.OpenAIClient(s).chat("system", "user")

    assert json.loads(out) == {"subject": "s", "body": "b"}
    assert sent["url"] == "https://example.test/v1/chat/completions"
    assert sent["headers"] == {"Authorization": "Bearer k"}
    assert sent["body"]["enable_thinking"] is False
    assert sent["body"]["model"] == "qwen-test"
