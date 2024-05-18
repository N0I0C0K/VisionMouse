from fastapi.testclient import TestClient

from server import app

test_client = TestClient(app)
