from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    Income: float
    Recency: float
    MntWines: float

    features_json: str = Field(default="{}")  # сырые признаки/вход
    created_at: datetime = Field(default_factory=datetime.utcnow)

    predictions: List["PredictionResult"] = Relationship(back_populates="customer")


class PredictionResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    customer_id: int = Field(foreign_key="customer.id")

    score: float
    label: int
    model_version: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional[Customer] = Relationship(back_populates="predictions")
