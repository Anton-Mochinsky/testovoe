import pytest
from fastapi.testclient import TestClient
from main import app



client = TestClient(app)

def test_create_meme():
    response = client.post("/memes", json={"text": "Test Text", "image_url": "https://example.com/image.png"})
    assert response.status_code == 200
    assert response.json()["text"] == "Test Text"

def test_get_meme():
    response = client.post("/memes", json={"text": "Test Text", "image_url": "https://example.com/image.png"})
    meme_id = response.json()["id"]
    response = client.get(f"/memes/{meme_id}")
    assert response.status_code == 200
    assert response.json()["text"] == "Test Text"

def test_update_meme():
    response = client.post("/memes", json={"text": "Test Text", "image_url": "https://example.com/image.png"})
    meme_id = response.json()["id"]
    response = client.put(f"/memes/{meme_id}", json={"text": "Updated Text"})
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Text"

def test_get_memes():
    response = client.get("/memes")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_image():
    with open("test_image.png", "rb") as file:
        response = client.post("/images/upload", files={"file": ("test_image.png", file, "image/jpeg")})
    assert response.status_code == 200

def test_get_image():
    response = client.post("/images/upload", files={"file": ("test_image.png", open("test_image.png", "rb"), "image/jpeg")})
    image_id = response.json()["filename"]
    response = client.get(f"/images/{image_id}")
    assert response.status_code == 200
