from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_predict_endpoint():
  payload = {
      "Income": 40000,
      "Recency": 10,
      "MntWines": 200,
      # добавить остальные признаки, если они обязательные
  }

  response = client.post("/api/v1/predict", json=payload)
  assert response.status_code == 200

  data = response.json()
  assert "score" in data
  assert "label" in data
  assert 0.0 <= data["score"] <= 1.0
  assert data["label"] in [0, 1]
