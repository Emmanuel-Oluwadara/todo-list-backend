import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "todos.db"
    monkeypatch.setenv("TODO_DATABASE_PATH", str(db_path))

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_list_when_database_is_empty(client):
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_create_todo_and_trim_text(client):
    response = client.post("/api/todos", json={"text": "   Plan the week   "})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "text": "Plan the week",
        "completed": False,
    }


def test_reject_blank_and_overlong_text(client):
    blank_response = client.post("/api/todos", json={"text": "   "})
    long_response = client.post("/api/todos", json={"text": "x" * 161})

    assert blank_response.status_code == 422
    assert long_response.status_code == 422


def test_update_completion(client):
    created = client.post("/api/todos", json={"text": "Read a book"})
    todo_id = created.json()["id"]

    response = client.patch(f"/api/todos/{todo_id}", json={"completed": True})

    assert response.status_code == 200
    assert response.json() == {
        "id": todo_id,
        "text": "Read a book",
        "completed": True,
    }


def test_delete_one_todo_and_missing_id(client):
    created = client.post("/api/todos", json={"text": "Delete me"})
    todo_id = created.json()["id"]

    delete_response = client.delete(f"/api/todos/{todo_id}")
    missing_response = client.delete(f"/api/todos/{todo_id}")

    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


def test_clear_completed_todos_without_deleting_active_todos(client):
    first = client.post("/api/todos", json={"text": "Keep me"})
    second = client.post("/api/todos", json={"text": "Complete me"})
    second_id = second.json()["id"]

    client.patch(f"/api/todos/{second_id}", json={"completed": True})
    response = client.delete("/api/todos/completed")

    assert response.status_code == 200
    assert response.json() == {"deleted": 1}

    todos = client.get("/api/todos").json()
    assert len(todos) == 1
    assert todos[0] == first.json()


def test_persistence_across_separate_api_requests(client):
    client.post("/api/todos", json={"text": "Persist me"})
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == [{
        "id": 1,
        "text": "Persist me",
        "completed": False,
    }]
