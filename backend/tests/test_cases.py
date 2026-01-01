import pytest
import uuid
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
    random_id = uuid.uuid4()
    response = await client.get(f"/api/cases/{random_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_test_case(client):
    case = await TestCase.create(name="Old Name", url="http://old.com")
    
    payload = {
        "name": "New Name",
        "url": "http://new.com",
        "steps": [
            {"order": 1, "instruction": "New Step"}
        ]
    }
    
    response = await client.put(f"/api/cases/{case.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["url"] == "http://new.com"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["instruction"] == "New Step"

@pytest.mark.asyncio
async def test_delete_test_case(client):
    case = await TestCase.create(name="To Delete", url="http://delete.com")
    
    response = await client.delete(f"/api/cases/{case.id}")
    assert response.status_code == 204
    
    # Verify it's gone
    check = await TestCase.get_or_none(id=case.id)
    assert check is None
