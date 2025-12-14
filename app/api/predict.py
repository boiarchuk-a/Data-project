from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db import get_session
from app.models import Customer, PredictionResult
from app.schemas import PredictRequest, PredictResponse
from app.ml.inference import predict_single

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, session: Session = Depends(get_session)):
    # 1) сохраняем клиента
    customer = Customer(
        Income=payload.Income,
        Recency=payload.Recency,
        MntWines=payload.MntWines,
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)

    # 2) инференс
    proba, label, model_version = predict_single(payload)

    # 3) сохраняем результат предсказания
    pr = PredictionResult(
        customer_id=customer.id,
        score=proba,
        label=label,
        model_version=model_version,
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)

    # 4) возвращаем то, что ожидает схема ответа
    return PredictResponse(
        probability=proba,
        label=label,
        model_version=model_version,
        customer_id=customer.id,
        prediction_id=pr.id,
    )
