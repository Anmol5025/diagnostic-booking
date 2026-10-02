import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Diagnostic Booking Service API"}

@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    response = await client.post("/auth/signup", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # Need to signup first
    await client.post("/auth/signup", json={"email": "login@example.com", "password": "password123"})
    
    response = await client.post("/auth/login", data={"username": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
