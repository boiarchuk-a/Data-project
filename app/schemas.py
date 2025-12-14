from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    Income: float = Field(..., ge=0)
    Recency: float = Field(..., ge=0)
    MntWines: float = Field(..., ge=0)


class PredictResponse(BaseModel):
    probability: float
    label: int
    model_version: str
    customer_id: int
    prediction_id: int


class CustomerCreate(BaseModel):
    Income: float
    Recency: float
    MntWines: float


class CustomerRead(CustomerCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PredictionRead(BaseModel):
    id: int
    customer_id: int
    score: float
    label: int
    model_version: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
