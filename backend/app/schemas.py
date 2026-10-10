from pydantic import BaseModel, Field

class Questionnaire(BaseModel):
    anon_id: str = Field(min_length=8, max_length=64)
    pregnancies: float = Field(ge=0, le=20)
    glucose: float = Field(ge=40, le=300)
    blood_pressure: float = Field(ge=30, le=200)
    skin_thickness: float = Field(ge=5, le=100)
    insulin: float = Field(ge=10, le=900)
    bmi: float = Field(ge=10, le=70)
    pedigree: float = Field(ge=0.05, le=2.5)
    age: int = Field(ge=18, le=100)

class UserCreate(BaseModel):
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=72)