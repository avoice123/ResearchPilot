from fastapi.testclient import TestClient
from api import app
client = TestClient(app)
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
def test_agent_empty_question():
    response=client.post("agent/ask",
                         json={'question': ''}
                         )
    assert response.status_code == 422
def test_agent_ask_success(monkeypatch):
    def fake_ask(question):
        return "这是模拟回答"

    monkeypatch.setattr(
        "api.ask_with_tools",
        fake_ask
    )

    response = client.post(
        "/agent/ask",
        json={"question": "实验1的数据是什么？"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "这是模拟回答"
    }
def test_agent_ask_failure(monkeypatch):
    def fake_ask(question):
        raise RuntimeError("模拟qwen服务器故障")
    monkeypatch.setattr("api.ask_with_tools", fake_ask)
    response = client.post(
        "/agent/ask",
        json={"question":"实验1的数据是什么?"}
    )
    assert response.status_code == 502
    assert response.json() == {"detail":"Agent service failed"}
def test_agent_ask_argument(monkeypatch):
    received={}
    def fake_ask(question):
        received["question"]=question
        return "模拟回答"
    monkeypatch.setattr("api.ask_with_tools", fake_ask)
    response = client.post(
        "/agent/ask",
        json={"question":"fkall"}
    )
    assert response.status_code == 200
    assert response.json() == {"answer":"模拟回答"}
    assert received["question"] == "fkall"