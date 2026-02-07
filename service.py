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

        dataAvaialble = yf.download(symbol.upper(), period="max", interval="1d", auto_adjust=False, progress=False)

        prices = dataAvaialble["Adj Close"].dropna()

        if len(prices) < 10:
            raise Exception("Not enough historical data")
        
        todayPrice = prices.iloc[-1]
        todayDate = prices.index[-1]

        def priceNowOrBefore(data):
            return prices.loc[:data].iloc[-1]
        
        def percentage(oldPrice):
            return round(((todayPrice - oldPrice) / oldPrice) * 100, 2)
        
        oneDayPrice = prices.iloc[-2]
        fiveDayPrice = prices.iloc[-6]

        oneMonthPrice = priceNowOrBefore(
            todayDate - pd.DateOffset(months=1)
        )

        sixMonthPrice = priceNowOrBefore(
            todayDate - pd.DateOffset(months=6)
        )

        ytdPrice = priceNowOrBefore(
            pd.Timestamp(year=todayDate.year, month=1, day=1)
        )

        oneYearPrice = priceNowOrBefore(
            todayDate - pd.DateOffset(years=1)
        )

        threeYearPrice = priceNowOrBefore(
            todayDate - pd.DateOffset(years=3)
        )

        fiveYearPrice = priceNowOrBefore(
            todayDate - pd.DateOffset(years=5)
        )

        tenYearPrice = priceNowOrBefore(
            todayDate - pd.DateOffset(years=10)
        )

        price_changes = {
            "one_Day": percentage(oneDayPrice),
            "five_Day": percentage(fiveDayPrice),
            "one_Month": percentage(oneMonthPrice),
            "six_Month": percentage(sixMonthPrice),
            "year_To_Date": percentage(ytdPrice),
            "one_Year": percentage(oneYearPrice),
            "three_Year": percentage(threeYearPrice),
            "five_Year": percentage(fiveYearPrice),
            "ten_Year": percentage(tenYearPrice)
        }
        

        return {
            "Metrics": metrics,
            "Target": targets,
            "priceChangePercentage": price_changes
        }

    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    

def safe(value):
    if value is None:
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
