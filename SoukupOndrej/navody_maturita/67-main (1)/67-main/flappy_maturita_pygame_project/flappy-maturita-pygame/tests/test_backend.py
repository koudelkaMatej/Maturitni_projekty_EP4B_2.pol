import sys
from pathlib import Path
import importlib

import pytest


SERVER_DIR = Path(__file__).resolve().parent.parent / "server"
sys.path.insert(0, str(SERVER_DIR))

db = importlib.import_module("db")
app_module = importlib.import_module("app")


@pytest.fixture
def client(tmp_path):
    test_db_path = tmp_path / "test_flappy.db"
    db.DB_PATH = test_db_path
    db.SCHEMA_PATH = SERVER_DIR / "schema.sql"

    db.init_db()

    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        yield client


def test_register_and_login(client):
    res = client.post("/api/register", json={
        "username": "ondra",
        "password": "heslo123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["username"] == "ondra"

    res = client.post("/api/login", json={
        "username": "ondra",
        "password": "heslo123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["username"] == "ondra"


def test_score_is_saved_once_per_user_and_difficulty(client):
    res = client.post("/api/register", json={
        "username": "ondra",
        "password": "heslo123"
    })
    assert res.status_code == 200

    res = client.post("/api/scores", json={
        "username": "ondra",
        "difficulty": "normal",
        "score": 5
    })
    assert res.status_code == 200

    res = client.post("/api/scores", json={
        "username": "ondra",
        "difficulty": "normal",
        "score": 3
    })
    assert res.status_code == 200

    res = client.post("/api/scores", json={
        "username": "ondra",
        "difficulty": "normal",
        "score": 8
    })
    assert res.status_code == 200

    res = client.get("/api/scores?difficulty=normal&limit=10")
    assert res.status_code == 200
    data = res.get_json()

    assert data["difficulty"] == "normal"
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "ondra"
    assert data["items"][0]["score"] == 8