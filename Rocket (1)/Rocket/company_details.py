import os
import time
import requests

API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

TICKERS = [
    "601899.SS",  # Zijin Mining
    "601088.SS",  # China Shenhua Energy
    "603993.SS",  # CMOC Group
    "601600.SS",  # Aluminum Corp of China
    "600111.SS",  # China Northern Rare Earth
]

def fetch_quote(symbol: str) -> dict:
    r = requests.get(BASE_URL, params={
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }).json()

    gq = r.get("Global Quote", {})
    if not gq:
        return {"ticker": symbol, "error": "No data returned"}

    return {
        "ticker": gq.get("01. symbol"),
        "last_price": float(gq.get("05. price", 0)),
        "previous_close": float(gq.get("08. previous close", 0)),
        "change": float(gq.get("09. change", 0)),
        "change_percent": gq.get("10. change percent", ""),
        "volume": int(gq.get("06. volume", 0)),
        "latest_trading_day": gq.get("07. latest trading day", ""),
    }

if __name__ == "__main__":
    for ticker in TICKERS:
        result = fetch_quote(ticker)
        print(result)
        time.sleep(1.5)  # respect rate limit