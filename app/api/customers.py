from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import Customer, PredictionResult
from app.schemas import CustomerCreate, CustomerRead, PredictionRead

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead)
def create_customer(payload: CustomerCreate, session: Session = Depends(get_session)):
    customer = Customer(**payload.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("", response_model=List[CustomerRead])
def list_customers(session: Session = Depends(get_session), limit: int = 100, offset: int = 0):
    return session.exec(select(Customer).offset(offset).limit(limit)).all()


@router.get("/{customer_id}/predictions", response_model=List[PredictionRead])
def list_predictions(customer_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(PredictionResult)
        .where(PredictionResult.customer_id == customer_id)
        .order_by(PredictionResult.created_at.desc())
    )
    return session.exec(stmt).all()
