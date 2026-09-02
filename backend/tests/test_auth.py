def test_register_user_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "strongpassword123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert "password_hash" not in data
    assert "id" in data


def test_register_duplicate_email_fails(client):
    client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "strongpassword123"},
    )

    response = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "anotherpassword456"},
    )

    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "correctpassword"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "correctpassword"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "correctpassword"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_login_nonexistent_user_fails(client):
    response = client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "whatever123"},
    )

    assert response.status_code == 401


def test_login_returns_refresh_token(client):
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "refresh_token" in data


def test_refresh_token_issues_new_access_token(client):
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_access_token_rejected_at_refresh_endpoint(client):
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )
    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401


def test_refresh_token_rejected_at_protected_route(client):
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "carol@example.com", "password": "strongpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401