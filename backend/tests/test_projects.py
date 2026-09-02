def register_and_login(client, email: str, password: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_users_me_requires_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_users_me_with_valid_token(client):
    token = register_and_login(client, "alice@example.com", "strongpassword123")

    response = client.get("/users/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_users_me_with_invalid_token(client):
    response = client.get("/users/me", headers=auth_headers("garbage-token"))
    assert response.status_code == 401


def test_create_project_requires_auth(client):
    response = client.post("/projects/", json={"name": "Test Project"})
    assert response.status_code == 401


def test_create_and_list_project(client):
    token = register_and_login(client, "alice@example.com", "strongpassword123")

    create_response = client.post(
        "/projects/",
        json={"name": "My Project"},
        headers=auth_headers(token),
    )
    assert create_response.status_code == 201
    project = create_response.json()
    assert project["name"] == "My Project"

    list_response = client.get("/projects/", headers=auth_headers(token))
    assert list_response.status_code == 200
    projects = list_response.json()
    assert len(projects) == 1
    assert projects[0]["id"] == project["id"]


def test_user_cannot_access_another_users_project(client):
    token_a = register_and_login(client, "alice@example.com", "strongpassword123")
    token_b = register_and_login(client, "bob@example.com", "anotherpassword456")

    create_response = client.post(
        "/projects/",
        json={"name": "Alice's Project"},
        headers=auth_headers(token_a),
    )
    project_id = create_response.json()["id"]

    response = client.get(f"/projects/{project_id}", headers=auth_headers(token_b))

    assert response.status_code == 403


def test_user_project_list_is_isolated(client):
    token_a = register_and_login(client, "alice@example.com", "strongpassword123")
    token_b = register_and_login(client, "bob@example.com", "anotherpassword456")

    client.post("/projects/", json={"name": "Alice's Project"}, headers=auth_headers(token_a))

    response = client.get("/projects/", headers=auth_headers(token_b))

    assert response.status_code == 200
    assert response.json() == []


def test_get_nonexistent_project_returns_404(client):
    token = register_and_login(client, "alice@example.com", "strongpassword123")

    response = client.get("/projects/9999", headers=auth_headers(token))

    assert response.status_code == 404