from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")

class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    anon_id: Mapped[str] = mapped_column(String, index=True)
    pregnancies: Mapped[float] = mapped_column(Float)
    glucose: Mapped[float] = mapped_column(Float)
    blood_pressure: Mapped[float] = mapped_column(Float)
    skin_thickness: Mapped[float] = mapped_column(Float)
    insulin: Mapped[float] = mapped_column(Float)
    bmi: Mapped[float] = mapped_column(Float)
    pedigree: Mapped[float] = mapped_column(Float)
    age: Mapped[int] = mapped_column(Integer)
    probability: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)