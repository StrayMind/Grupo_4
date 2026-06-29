from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from app.db import test_connection, get_fraudtest, get_fraudtest_stats
from app.predict import predict_fraude

app = FastAPI(title="MVP Fraud Test")

class PredictFraudeRequest(BaseModel):
    merchant: str
    category: str
    amt: float
    street: str
    city: str
    state: str
    zip: int
    lat: float
    long: float
    job: str
    merch_lat: float
    merch_long: float

@app.get("/")
def root():
    return {"message": "API MVP Fraud Test activa"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-health")
def db_health():
    return test_connection()

@app.get("/fraudtest-demo")
def fraudtest_demo(limit: int = Query(default=20, ge=1, le=100)):
    try:
        data = get_fraudtest(limit=limit)
        return {
            "status": "ok",
            "count": len(data),
            "limit": limit,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fraudtest-demo/stats")
def fraudtest_demo_stats():
    try:
        stats = get_fraudtest_stats()
        return {
            "status": "ok",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-fraude")
def predict_fraude_endpoint(payload: PredictFraudeRequest):
    try:
        result = predict_fraude(payload.model_dump())
        return {
            "status": "ok",
            "prediction": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
