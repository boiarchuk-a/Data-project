from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import Customer, PredictionResult
from app.schemas import PredictRequest, PredictResponse
from app.ml.inference import predict_single

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest, request: Request, session: Session = Depends(get_session)):
    # 1) сохраняем клиента
    customer = Customer(
        Income=payload.Income,
        Recency=payload.Recency,
        MntWines=payload.MntWines,
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)

    # 2) инференс (через RMQ, если включено; иначе локально)
    payload_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()

    rpc = getattr(request.app.state, "rpc", None)
    if rpc is not None:
        try:
            rmq_resp = await rpc.predict(payload_dict, timeout=10.0)
            proba = rmq_resp["score"]
            label = rmq_resp["label"]
            model_version = rmq_resp["model_version"]
        except Exception:
            # fallback если RMQ временно недоступен
            proba, label, model_version = predict_single(payload)
    else:
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
