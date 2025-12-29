import pytest
from backend.app.models.test_case import TestCase

@pytest.mark.asyncio
async def test_create_test_case(client):
    payload = {
        "name": "Test Google Search",
        "url": "https://google.com",
        "steps": [
            {"order": 1, "instruction": "Type 'WebuiTester' into search bar"},
            {"order": 2, "instruction": "Click Search"}
        ]
    }
    response = await client.post("/api/cases", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert len(data["steps"]) == 2
    assert "id" in data

@pytest.mark.asyncio
async def test_get_test_cases(client):
    # Create one first
    await TestCase.create(name="List Test", url="http://list.com")
    
    response = await client.get("/api/cases")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_single_case(client):
    case = await TestCase.create(name="Single Test", url="http://single.com")
    
    response = await client.get(f"/api/cases/{case.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(case.id)
    assert data["name"] == "Single Test"

@pytest.mark.asyncio
async def test_get_non_existent_case(client):
    import uuid
    random_id = uuid.uuid4()
    response = await client.get(f"/api/cases/{random_id}")
    assert response.status_code == 404
