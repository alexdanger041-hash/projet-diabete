import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas
from .auth import hash_password, verify_password, create_token, current_user, admin_only
from .database import engine, get_db, SessionLocal
from .predict import predire

models.Base.metadata.create_all(bind=engine)

def creer_admin():
    db = SessionLocal()
    email = os.getenv("ADMIN_EMAIL", "admin@diabete.local")
    if not db.query(models.User).filter(models.User.email == email).first():
        db.add(models.User(email=email, role="admin",
                           password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "Admin1234!"))))
        db.commit()
    db.close()

creer_admin()

AVERTISSEMENT = ("Outil pédagogique de sensibilisation : estimation statistique, "
                 "pas un diagnostic médical. Consultez un professionnel de santé.")

app = FastAPI(title="Diabète - outil pédagogique de sensibilisation")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:4173").split(","),
    allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def accueil():
    return {"message": "API en marche.", "avertissement": AVERTISSEMENT}

@app.post("/auth/register")
def register(u: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == u.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    db.add(models.User(email=u.email, password_hash=hash_password(u.password), role="user"))
    db.commit()
    return {"message": "Compte créé"}

@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    return {"access_token": create_token(user.email, user.role),
            "token_type": "bearer", "role": user.role}

@app.post("/predict")
def predict(q: schemas.Questionnaire, db: Session = Depends(get_db),
            user: models.User = Depends(current_user)):
    proba, niveau, facteurs, recos = predire(
        [q.pregnancies, q.glucose, q.blood_pressure, q.skin_thickness,
         q.insulin, q.bmi, q.pedigree, q.age])
    db.add(models.Prediction(
        anon_id=q.anon_id, pregnancies=q.pregnancies, glucose=q.glucose,
        blood_pressure=q.blood_pressure, skin_thickness=q.skin_thickness,
        insulin=q.insulin, bmi=q.bmi, pedigree=q.pedigree, age=q.age,
        probability=proba, risk_level=niveau))
    db.commit()
    return {"probabilite": round(proba, 3), "niveau": niveau, "facteurs": facteurs,
            "recommandations": recos, "avertissement": AVERTISSEMENT}

@app.get("/history")
def history(anon_id: str, db: Session = Depends(get_db),
            user: models.User = Depends(current_user)):
    lignes = (db.query(models.Prediction)
              .filter(models.Prediction.anon_id == anon_id)
              .order_by(models.Prediction.created_at.desc()).all())
    return [{"date": l.created_at, "probabilite": round(l.probability, 3),
             "niveau": l.risk_level, "glucose": l.glucose, "bmi": l.bmi, "age": l.age}
            for l in lignes]

@app.get("/admin/dashboard")
def dashboard(db: Session = Depends(get_db), admin: models.User = Depends(admin_only)):
    P = models.Prediction
    total = db.query(func.count(P.id)).scalar()
    par_niveau = dict(db.query(P.risk_level, func.count(P.id)).group_by(P.risk_level).all())
    moy = db.query(func.avg(P.glucose), func.avg(P.bmi), func.avg(P.age),
                   func.avg(P.probability)).one()
    return {"total_predictions": total, "par_niveau": par_niveau,
            "moyennes": {"glucose": round(moy[0] or 0, 1), "bmi": round(moy[1] or 0, 1),
                         "age": round(moy[2] or 0, 1), "probabilite": round(moy[3] or 0, 3)}}