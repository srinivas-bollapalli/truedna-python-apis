"""
Authentication endpoint tests.

NOTE: These tests require a live MongoDB connection (truadnaDev database)
      with at least one seeded user.  Run seed_data.py first.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

# Credentials matching seed_data.py sample users
TEST_USER = {"username": "test_user", "password": "Test@3456"}


@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/auth/login", json=TEST_USER)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/auth/login",
            json={"username": "test_user", "password": "wrongpass"},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_resp = await client.post("/api/auth/login", json=TEST_USER)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        me_resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == TEST_USER["username"]


@pytest.mark.asyncio
async def test_token_refresh():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_resp = await client.post("/api/auth/login", json=TEST_USER)
        refresh_token = login_resp.json()["refresh_token"]

        refresh_resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()


@pytest.mark.asyncio
async def test_logout():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_resp = await client.post("/api/auth/login", json=TEST_USER)
        token = login_resp.json()["access_token"]

        logout_resp = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_revoked_token_rejected():
    """After logout the old token must return 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_resp = await client.post("/api/auth/login", json=TEST_USER)
        token = login_resp.json()["access_token"]

        await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        me_resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert me_resp.status_code == 401
