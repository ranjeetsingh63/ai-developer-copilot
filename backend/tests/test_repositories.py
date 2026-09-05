import pytest


# --- Helper Functions ---
def create_user_and_get_token(client, email: str, password: str = "securepassword") -> str:
    """Helper to register and login a user, returning their access token."""
    client.post("/auth/register", json={"email": email, "password": password})
    # Changed from `data={"username"...}` to `json={"email"...}`
    res = client.post("/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def create_project(client, token: str, name: str = "Test Project") -> dict:
    """Helper to create a project for a user."""
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/projects/", json={"name": name}, headers=headers)
    return res.json()


# --- Tests ---
def test_create_repository_success(client):
    token = create_user_and_get_token(client, "repo_owner@example.com")
    project = create_project(client, token)

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "github_url": "https://github.com/ranjeetsingh63/ai-developer-copilot",
        "name": "ai-developer-copilot",
        "default_branch": "main"
    }

    res = client.post(f"/projects/{project['id']}/repositories/", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "ai-developer-copilot"
    assert "id" in data
    assert data["project_id"] == project["id"]


def test_create_repository_invalid_url(client):
    token = create_user_and_get_token(client, "bad_url@example.com")
    project = create_project(client, token)

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "github_url": "http://not-a-valid-github-url.com/repo",
        "name": "invalid-repo",
        "default_branch": "main"
    }

    res = client.post(f"/projects/{project['id']}/repositories/", json=payload, headers=headers)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "validation_error"


def test_create_repository_404_project_not_found(client):
    token = create_user_and_get_token(client, "no_project@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "github_url": "https://github.com/test/repo",
        "name": "repo",
        "default_branch": "main"
    }

    # Attempting to add to a project ID that does not exist
    res = client.post("/projects/9999/repositories/", json=payload, headers=headers)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "not_found"


def test_create_repository_403_not_owner(client):
    # User A creates a project
    token_a = create_user_and_get_token(client, "user_a@example.com")
    project_a = create_project(client, token_a)

    # User B logs in
    token_b = create_user_and_get_token(client, "user_b@example.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    payload = {
        "github_url": "https://github.com/test/repo",
        "name": "repo",
        "default_branch": "main"
    }

    # User B tries to add a repository to User A's project
    res = client.post(f"/projects/{project_a['id']}/repositories/", json=payload, headers=headers_b)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "forbidden"


def test_get_repositories_paginated(client):
    token = create_user_and_get_token(client, "pagi@example.com")
    project = create_project(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    # Create 2 repositories
    client.post(f"/projects/{project['id']}/repositories/",
                json={"github_url": "https://github.com/test/repo1", "name": "repo1", "default_branch": "main"},
                headers=headers)
    client.post(f"/projects/{project['id']}/repositories/",
                json={"github_url": "https://github.com/test/repo2", "name": "repo2", "default_branch": "main"},
                headers=headers)

    # Fetch with limit=1 to test pagination
    res = client.get(f"/projects/{project['id']}/repositories/?limit=1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1