"""Tests for the BaseAgent HTTP surface (agent card, discovery, JSON-RPC)."""


def test_agent_card_endpoint(math_client):
    resp = math_client.get("/")
    assert resp.status_code == 200
    card = resp.json()
    assert card["name"] == "Math Agent"
    assert card["id"] == "math-agent-001"
    assert "statistical_analysis" in card["capabilities"]
    assert card["connection"]["url"].endswith(":8001")


def test_well_known_discovery_path(math_client):
    resp = math_client.get("/.well-known/agent.json")
    assert resp.status_code == 200
    assert resp.json()["id"] == "math-agent-001"


def test_health_endpoint(data_client):
    resp = data_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["agentId"] == "data-analyst-agent-001"


def test_unknown_method_returns_method_not_found(math_client):
    payload = {"id": "z", "jsonrpc": "2.0", "method": "does/not/exist", "params": {}}
    resp = math_client.post("/", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["error"]["code"] == -32601


def test_task_get_unknown_task_returns_invalid_params(math_client):
    payload = {"id": "z", "jsonrpc": "2.0", "method": "task/get", "params": {"taskId": "nope"}}
    resp = math_client.post("/", json=payload)
    assert resp.json()["error"]["code"] == -32602


def test_message_send_returns_completed_task(math_client, jsonrpc_message):
    resp = math_client.post("/", json=jsonrpc_message("calculate mean of [2, 4, 6]"))
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert result["kind"] == "task"
    assert result["status"]["state"] == "completed"
    assert "Mean: 4.0000" in result["status"]["message"]["parts"][0]["text"]


def test_task_is_retrievable_after_send(math_client, jsonrpc_message):
    send = math_client.post("/", json=jsonrpc_message("calculate mean of [10, 20]"))
    task_id = send.json()["result"]["id"]
    get = math_client.post(
        "/", json={"id": "g", "jsonrpc": "2.0", "method": "task/get", "params": {"taskId": task_id}}
    )
    assert get.json()["result"]["id"] == task_id
