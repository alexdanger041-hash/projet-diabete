import os
import uuid
os.environ["DATABASE_URL"] = "sqlite:///./test_diabete.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALIDE = {
    "anon_id": "test-12345678", "pregnancies": 2, "glucose": 150,
    "blood_pressure": 80, "skin_thickness": 30, "insulin": 120,
    "bmi": 33, "pedigree": 0.5, "age": 45,
}

def token(email=None, password="motdepasse1"):
    email = email or f"{uuid.uuid4().hex[:8]}@test.com"
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", data={"username": email, "password": password})
    return r.json()["access_token"]

def auth(t):
    return {"Authorization": f"Bearer {t}"}

def test_accueil_avec_avertissement():
    r = client.get("/")
    assert r.status_code == 200
    assert "pas un diagnostic médical" in r.json()["avertissement"]

def test_inscription_doublon_refusee():
    email = f"{uuid.uuid4().hex[:8]}@test.com"
    corps = {"email": email, "password": "motdepasse1"}
    assert client.post("/auth/register", json=corps).status_code == 200
    assert client.post("/auth/register", json=corps).status_code == 400

def test_connexion_mauvais_mot_de_passe():
    r = client.post("/auth/login", data={"username": "inconnu@test.com", "password": "xxxxxxxx"})
    assert r.status_code == 401

def test_predict_sans_token_refuse():
    assert client.post("/predict", json=VALIDE).status_code == 401

def test_predict_valide():
    r = client.post("/predict", json=VALIDE, headers=auth(token()))
    assert r.status_code == 200
    d = r.json()
    assert 0 <= d["probabilite"] <= 1
    assert d["niveau"] in ("faible", "modéré", "élevé")
    assert len(d["facteurs"]) == 8
    assert "avertissement" in d

def test_predict_valeur_invalide():
    mauvais = {**VALIDE, "glucose": 5000}
    r = client.post("/predict", json=mauvais, headers=auth(token()))
    assert r.status_code == 422

def test_historique_enregistre():
    t = token()
    client.post("/predict", json={**VALIDE, "anon_id": "hist-unique-001"}, headers=auth(t))
    r = client.get("/history", params={"anon_id": "hist-unique-001"}, headers=auth(t))
    assert r.status_code == 200 and len(r.json()) >= 1

def test_dashboard_interdit_a_un_utilisateur():
    assert client.get("/admin/dashboard", headers=auth(token())).status_code == 403

def test_dashboard_autorise_a_ladmin():
    t = token("admin@diabete.local", "Admin1234!")
    r = client.get("/admin/dashboard", headers=auth(t))
    assert r.status_code == 200
    assert "total_predictions" in r.json()