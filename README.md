# Risque de diabète : outil pédagogique de sensibilisation

>  Prototype pédagogique de sensibilisation. Il fournit une estimation statistique. 

## Fonctionnalités
- Questionnaire et estimation statistique du risque
- Affichage des facteurs d'influence (SHAP) et recommandations générales
- Historique anonyme
- Dashboard agrégé (profil admin)
- Authentification JWT, 2 profils (utilisateur, admin)
- Application web React responsive et PWA

## Architecture
- `ml/` : exploration des données, baseline (Logistic Regression), Random Forest, XGBoost, SHAP
- `backend/` : API FastAPI, base PostgreSQL (SQLite en local), tests pytest
- `frontend/` : React (Vite), Recharts, PWA
- `docker-compose.yml` : db + api + web
- `.github/workflows/ci.yml` : tests, build, build Docker

## Données et modèles
Pima Indians Diabetes Dataset (768 lignes, 8 variables). Les valeurs à 0 de Glucose, BloodPressure, SkinThickness, Insulin et BMI sont traitées comme manquantes et imputées par la médiane.

| Modèle | Accuracy | Recall | F1 | ROC-AUC |
|---|---|---|---|---|
| Logistic Regression (baseline) | 0,708 | 0,500 | 0,545 | 0,813 |
| Random Forest | 0,740 | 0,759 | 0,672 | 0,822 |
| XGBoost (retenu) | 0,766 | 0,722 | 0,684 | 0,823 |

Limites : dataset petit, une seule population, valeurs manquantes imputées.

## Lancer avec Docker
```
docker compose up --build
```
- Site : http://localhost:3000
- API et Swagger : http://localhost:8000/docs
- Compte admin par défaut : `admin@diabete.local` / `Admin1234!` (à changer via `ADMIN_EMAIL` et `ADMIN_PASSWORD`)

## Lancer en local sans Docker
```
# API
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Site
cd frontend
npm install
npm run dev
```

## Tests
```
cd backend
pytest -v
```