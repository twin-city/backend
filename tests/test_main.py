from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "listen"}

def test_generate():
    x1, y1, x2, y2 = 48.86440000000001, 2.3977, 48.865500000000004, 2.3994
    crs = 'EPSG:4326'
    response = client.get(f"/generate/?x1={x1}&y1={y1}&x2={x2}&y2={y2}&job=false&crs={crs}")
    response.json() == {'status': 'OK', 'job_name': '6cc135f46b8a4116edbadbaefe1333197dd8110a', 'url': 'https://6cc135f46b8a4116edbadbaefe1333197dd8110a.s3-website.fr-par.scw.cloud', 'warning': 'no job launched'}
