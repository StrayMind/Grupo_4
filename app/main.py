from fastapi import FastAPI, HTTPException, Query
from app.db import test_connection, get_fraudtest, get_fraudtest_stats

app = FastAPI(title="MVP Fraud Test")

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
        return {"status": "ok", "count": len(data), "limit": limit, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fraudtest-demo/stats")
def fraudtest_demo_stats():
    try:
        stats = get_fraudtest_stats()
        return {"status": "ok", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))