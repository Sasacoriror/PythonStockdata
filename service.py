import yfinance as yf
from fastapi import HTTPException


def getStockData(symbol: str):
    
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        metrics = {
            "symbol": safe(info.get("symbol")),
            "market_cap": safe(info.get("marketCap")),
            "trailing_eps": safe(info.get("trailingEps")),
            "forward_eps": safe(info.get("forwardEps")),
            "pe_ratio": safe(info.get("trailingPE")),
            "forward_pe": safe(info.get("forwardPE")),
            "beta": safe(info.get("beta")),
            "price": safe(info.get("currentPrice")),
            "currency": safe(info.get("currency")),
        }

        current = info.get("currentPrice")
        mean_target = info.get("targetMeanPrice")

        upside = None

        if current and mean_target:
            upside = round((mean_target - current) / current * 100, 2)

        targets = {
            "symbol": safe(symbol.upper()),
            "current_price": safe(current),
            "target_mean": safe(mean_target),
            "target_low": safe(info.get("targetLowPrice")),
            "target_high": safe(info.get("targetHighPrice")),
            "analyst_count": safe(info.get("numberOfAnalystOpinions")),
            "recommendation_mean": safe(info.get("recommendationMean")),   # 1=Strong Buy ... 5=Sell
            "recommendation_key": safe(info.get("recommendationKey")),     # buy / hold / sell
            "implied_upside_pct": safe(upside),
        }

        return {
            "metrics": metrics,
            "target": targets
        }

    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    

def safe(value):
    if value is None:
        return None
    if hasattr(value, "item"):
        return value.item()
    return value