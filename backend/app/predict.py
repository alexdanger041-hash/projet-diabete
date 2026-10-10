import joblib
import pandas as pd
import shap
from pathlib import Path

PIPE = joblib.load(Path(__file__).parent / "model.joblib")
IMPUTER = PIPE.named_steps["imputer"]
EXPLAINER = shap.TreeExplainer(PIPE.named_steps["model"])
COLS = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
        "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]

RECOS = {
    "Glucose": "Limitez les sucres et boissons sucrées ; un bilan de glycémie auprès d'un professionnel de santé est conseillé.",
    "BMI": "Une activité physique régulière et une alimentation équilibrée aident à maintenir un poids de santé.",
    "Age": "Le risque augmente avec l'âge : un suivi médical régulier est recommandé.",
    "Pregnancies": "Parlez de vos antécédents de grossesse à votre médecin lors de vos bilans.",
    "BloodPressure": "Faites contrôler régulièrement votre tension artérielle.",
    "Insulin": "Un bilan sanguin complet permet de mieux comprendre ces valeurs.",
    "SkinThickness": "Une alimentation équilibrée et de l'activité physique restent bénéfiques.",
    "DiabetesPedigreeFunction": "Avec des antécédents familiaux, un dépistage régulier est conseillé.",
}

def niveau(p: float) -> str:
    return "faible" if p < 0.33 else "modéré" if p < 0.6 else "élevé"

def predire(valeurs: list):
    df = pd.DataFrame([valeurs], columns=COLS)
    proba = float(PIPE.predict_proba(df)[0, 1])
    X = pd.DataFrame(IMPUTER.transform(df), columns=COLS)
    sv = EXPLAINER.shap_values(X)[0]
    facteurs = sorted(
        [{"variable": c, "valeur": float(X[c].iloc[0]), "impact": float(s)}
         for c, s in zip(COLS, sv)],
        key=lambda f: abs(f["impact"]), reverse=True)
    recos = [RECOS[f["variable"]] for f in facteurs if f["impact"] > 0][:3]
    if not recos:
        recos = ["Maintenez une alimentation équilibrée et une activité physique régulière."]
    return proba, niveau(proba), facteurs, recos