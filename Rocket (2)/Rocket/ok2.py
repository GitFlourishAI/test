from agents import function_tool
from httpx._transports import base
import numpy as np
from scipy.stats import truncnorm
from alpha import AlphaVantageClient


@function_tool

def income_statement(symbol:str,sensitivities:float):


    client = AlphaVantageClient()
    data = client.get_INCOME_STATEMENT(symbol)

    annual_reports = data.get("annualReports", [])

    np_sims = 10000

# Baseline revenue (USD)
    baseline_revenue = float(annual_reports[0]["totalRevenue"])

# Shock distribution (revenue % change)
    mu = sensitivities
    sigma = 0.02
    lower = -0.08
    upper = 0.04

    a = (lower - mu) / sigma
    b = (upper - mu) / sigma

    shock = truncnorm.rvs(a, b, loc=mu, scale=sigma, size=np_sims)

# Revenue change
    delta_revenue = baseline_revenue * shock

# Financial parameters
    ebitda_margin = float(annual_reports[0]["ebitda"])/baseline_revenue
    tax_rate = 0.134
    discount_rate = 0.034
    years = 3
    delta_ebitda = delta_revenue * ebitda_margin

# After-tax impact
    after_tax_impact = delta_ebitda * (1 - tax_rate)

# Discounted valuation impact
    valuation_impact = after_tax_impact / ((1 + discount_rate) ** years)

# EBITDA delta change

    ebitda_change_pct = (delta_ebitda/float(annual_reports[0]["ebitda"]))*100

# Revenue delta change

    revenue_change_pct = delta_revenue/baseline_revenue*100


    return  f"\nvaluation Impact: {np.mean(valuation_impact):,.0f}", f"ebitda_impact: {ebitda_change_pct}", f"revenue_impact:{revenue_change_pct}"





