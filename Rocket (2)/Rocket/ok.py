import os
import time
import requests
from agents import function_tool
from typing import Dict
from financetoolkit import Toolkit

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
FMP_KEY = os.environ.get("FMP_API_KEY")
AV_BASE_URL = "https://www.alphavantage.co/query"

TICKERS = [
    "AAPL", "MSFT", "GOOGL"
]


def av_to_fmp_ticker(symbol: str) -> str:
    """Convert Alpha Vantage .SS suffix to FMP .SH suffix."""
    if symbol.endswith(".SS"):
        return symbol.replace(".SS", ".SH")
    return symbol


def fetch_quote(symbol: str) -> dict:
    r = requests.get(AV_BASE_URL, params={
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_KEY
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


def fetch_fmp_fundamentals(symbol: str) -> dict:
    """Fetch fundamentals from FMP via financetoolkit."""
    fmp_ticker = av_to_fmp_ticker(symbol)

    try:
        toolkit = Toolkit(
            tickers=[fmp_ticker],
            api_key=FMP_KEY,
            start_date="2023-01-01",
        )

        income = toolkit.get_income_statement()
        balance = toolkit.get_balance_sheet_statement()

        latest_year = income.columns[-1]

        revenue = float(income.loc["Revenue", latest_year])
        ebitda = float(income.loc["EBITDA", latest_year])
        tax_expense = float(income.loc["Income Tax Expense", latest_year])
        pretax_income = float(income.loc["Income Before Tax", latest_year])
        shares = float(income.loc["Weighted Average Shares Diluted", latest_year])

        total_debt = float(balance.loc["Total Debt", latest_year])
        net_debt = float(balance.loc["Net Debt", latest_year])

        ebitda_margin = ebitda / revenue if revenue else 0
        tax_rate = tax_expense / pretax_income if pretax_income else 0
        market_cap = last_price * shares
        enterprise_value = market_cap + net_debt
        ev_multiple = enterprise_value / ebitda

        return {
            "base_revenue": round(revenue, 2),
            "ebitda_margin": round(ebitda_margin, 4),
            "tax_rate": round(tax_rate, 4),
            "net_debt": round(net_debt, 2),
            "shares_outstanding": round(shares, 2),
            "ev_multiple": round(ev_multiple, 2),
        }

    except Exception as e:
        return {
            "error": str(e),
            "base_revenue": 0,
            "ebitda_margin": 0,
            "tax_rate": 0,
            "net_debt": 0,
            "shares_outstanding": 0,
            "ev_multiple": 0,
        }

def fetch_company_financials(symbol: str) -> Dict:
    """
    Fetches real-time price from Alpha Vantage and fundamental data from FMP.
    Returns: ticker, last_price, shares_outstanding, ev_multiple,
             base_revenue, ebitda_margin, tax_rate, net_debt.
    Does NOT return revenue_delta_pct, operating_leverage, or
    confidence_level — those come from agent reasoning.
    """
    quote = fetch_quote(symbol)
    fundamentals = fetch_fmp_fundamentals(symbol)

    return {
        "ticker": symbol,
        "last_price": quote.get("last_price"),
        "shares_outstanding": fundamentals.get("shares_outstanding"),
        "ev_multiple": fundamentals.get("ev_multiple"),
        "base_revenue": fundamentals.get("base_revenue"),
        "ebitda_margin": fundamentals.get("ebitda_margin"),
        "tax_rate": fundamentals.get("tax_rate"),
        "net_debt": fundamentals.get("net_debt"),
    }


fetch_company_financials_tool = function_tool(fetch_company_financials)




