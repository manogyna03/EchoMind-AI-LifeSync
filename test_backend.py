"""
Automated unit & integration verification for EchoMind AI backend.
Tests SQLite database persistence, task creation/retrieval, MCP compliance, and Assistant intent engine.
"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.seed import seed_initial_data

def test_full_system():
    # Explicitly run DB initialization & seeding
    init_db()
    seed_initial_data()

    client = TestClient(app)

    print("\n1. Testing Health Endpoint...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    health_data = r.json()
    assert health_data["status"] == "healthy"
    print("   [OK] Health check OK:", health_data)

    print("\n2. Testing Task Retrieval...")
    r = client.get("/api/tasks")
    assert r.status_code == 200
    initial_tasks = r.json()
    print(f"   [OK] Retrieved {len(initial_tasks)} tasks from SQLite")
    assert len(initial_tasks) > 0

    print("\n3. Testing Task Creation End-to-End...")
    new_task_payload = {
        "title": "Verify Alexa+ MCP integration and build demo",
        "description": "Integration test created through EchoMind automated test suite.",
        "priority": "high",
        "category": "work",
        "status": "pending",
        "due_date": "2026-10-23"
    }
    r = client.post("/api/tasks", json=new_task_payload)
    assert r.status_code == 201, f"Task creation failed: {r.text}"
    created_task = r.json()
    assert created_task["title"] == new_task_payload["title"]
    assert "id" in created_task
    task_id = created_task["id"]
    print("   [OK] Successfully created task in SQLite with ID:", task_id)

    print("\n4. Testing Task Retrieval by ID & Update...")
    r = client.get(f"/api/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["id"] == task_id

    # Update task to completed
    r = client.put(f"/api/tasks/{task_id}", json={"status": "completed"})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    print("   [OK] Task updated to 'completed' successfully")

    print("\n5. Testing Assistant Voice/Text Intent Engine...")
    voice_command = {"message": "add task Buy fresh fruit and granola", "voice_mode": True}
    r = client.post("/api/assistant/interact", json=voice_command)
    assert r.status_code == 200
    res = r.json()
    assert res["intent_detected"] == "create_task"
    assert "Buy fresh fruit and granola" in res["reply"]
    assert len(res["speech_text"]) > 0
    print("   [OK] Assistant voice command processed, speech synthesized string:", res["speech_text"])

    print("\n6. Testing Simulated Smart Home Devices (Strictly Labeled)...")
    r = client.get("/api/smarthome/devices")
    assert r.status_code == 200
    devices = r.json()
    assert len(devices) > 0
    for dev in devices:
        assert dev["is_simulated"] is True
        assert "[SIMULATION]" in dev["name"]
    print(f"   [OK] {len(devices)} simulated smart home devices verified with [SIMULATION] labels")

    print("\n7. Testing Alexa+ Model Context Protocol (MCP) Server...")
    # Test MCP initialize
    mcp_init = {
        "jsonrpc": "2.0",
        "id": "test-init-1",
        "method": "initialize",
        "params": {}
    }
    r = client.post("/mcp", json=mcp_init)
    assert r.status_code == 200
    init_res = r.json()
    assert "serverInfo" in init_res["result"]
    assert init_res["result"]["serverInfo"]["name"] == "echomind-alexa-mcp"
    print("   [OK] MCP initialize handshake verified")

    # Test MCP tools/list
    mcp_tools = {
        "jsonrpc": "2.0",
        "id": "test-tools-1",
        "method": "tools/list",
        "params": {}
    }
    r = client.post("/mcp", json=mcp_tools)
    assert r.status_code == 200
    tools_list = r.json()["result"]["tools"]
    tool_names = [t["name"] for t in tools_list]
    print(f"   [OK] MCP tools discovered ({len(tools_list)} tools):", tool_names)
    assert "echomind_create_task" in tool_names

    # Test MCP tools/call
    mcp_call = {
        "jsonrpc": "2.0",
        "id": "test-call-1",
        "method": "tools/call",
        "params": {
            "name": "echomind_create_task",
            "arguments": {
                "title": "MCP Agent Autonomous Task",
                "priority": "high",
                "category": "work"
            }
        }
    }
    r = client.post("/mcp", json=mcp_call)
    assert r.status_code == 200
    call_res = r.json()
    assert call_res["result"]["isError"] is False
    print("   [OK] MCP tool 'echomind_create_task' called successfully:", call_res["result"]["content"][0]["text"])

    print("\n8. Testing Web Interface / SPA Delivery...")
    r = client.get("/")
    assert r.status_code == 200, f"Root SPA delivery failed: {r.status_code}"
    assert "EchoMind AI" in r.text
    assert "LifeSync Intelligence" in r.text
    print("   [OK] Web dashboard served successfully with HTML and voice-first UI")

    print("\n========================================================")
    print(" ALL BACKEND & MCP INTEGRATION TESTS PASSED 100%!")
    print("========================================================")

if __name__ == "__main__":
    test_full_system()
