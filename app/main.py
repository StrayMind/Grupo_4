from fastapi import FastAPI

app = FastAPI(title="MVP Fraud Test")

@app.get("/")
def root():
    return {"message": "API MVP Fraud Test activa"}

@app.get("/health")
def health():
    return {"status": "ok"}