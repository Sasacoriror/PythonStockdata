from fastapi import FastAPI
from service import getStockData

app = FastAPI(title="stock Analysis API")

@app.get("/stock/{symbol}")
def getStock(symbol: str):
    return getStockData(symbol)

@app.get("/health")
def health():
    return {"status": "ok"}