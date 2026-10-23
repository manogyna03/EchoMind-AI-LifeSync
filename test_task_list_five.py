import pytest
from app.models import Task

def test_task_list_five(client, auth_headers, db_session):
    # Create exactly five pending tasks with mixed priorities
    tasks_data = [
        ("Prepare slides", "high"),
        ("Buy groceries", "low"),
        ("Schedule meeting", "medium"),
        ("Read article", "low"),
        ("Update repo", "high"),
    ]
    for title, priority in tasks_data:
        db_session.add(Task(title=title, priority=priority, status="pending", user_id=auth_headers["user"]))
    db_session.commit()

    resp = client.post(
        "/api/assistant/interact",
        json={"message": "What are my tasks?"},
        headers=auth_headers,
    )
    data = resp.json()

    # Ensure exactly five task lines in reply
    assert data["reply"].count("\n") == 5
    for i, (title, priority) in enumerate(tasks_data, start=1):
        assert f"{i}. {title} (priority: {priority})" in data["reply"]

    # Speech must contain all five titles in priority order (high → medium → low)
    speech = data["speech_text"]
    # Expected order after sorting
    expected_order = ["Prepare slides", "Update repo", "Schedule meeting", "Buy groceries", "Read article"]
    for idx, title in enumerate(expected_order, start=1):
        assert f"{idx}. {title}" in speech
