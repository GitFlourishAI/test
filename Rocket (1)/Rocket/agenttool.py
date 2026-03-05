from agents import function_tool
from typing import Dict

# -------------------------------
# CORE FINANCIAL TRANSMISSION LOGIC
# -------------------------------

@function_tool
def compute_financial_impact(
    revenue_delta_pct: float,
    ebitda_margin: float,
    operating_leverage: float,
    tax_rate: float,
    net_debt: float,
    shares_outstanding: float,
    ev_multiple: float,
    base_revenue: float,
    confidence_level: float
) -> Dict:
    """
    Deterministic financial transmission engine.

    Parameters
    ----------
    revenue_delta_pct : % change in revenue (e.g., 0.03 for +3%)
    ebitda_margin : baseline EBITDA margin (e.g., 0.25)
    operating_leverage : EBITDA sensitivity multiplier (1.2–2.0 typical)
    tax_rate : corporate tax rate (e.g., 0.25)
    net_debt : company net debt
    shares_outstanding : total shares
    ev_multiple : EV/EBITDA multiple
    base_revenue : baseline annual revenue
    confidence_level : 0–100

    Returns
    -------
    Dict of deterministic outputs
    """

    # 1️⃣ Revenue Impact
    revenue_change = base_revenue * revenue_delta_pct

    # 2️⃣ EBITDA Impact (operating leverage effect)
    ebitda_change = revenue_change * ebitda_margin * operating_leverage

    # 3️⃣ FCF Impact (after tax simplification)
    fcf_change = ebitda_change * (1 - tax_rate)

    # 4️⃣ Valuation Impact via EV multiple
    enterprise_value_change = ebitda_change * ev_multiple

    # 5️⃣ Equity value impact
    equity_value_change = enterprise_value_change - 0  # debt static assumption

    # 6️⃣ Per share impact
    price_impact = equity_value_change / shares_outstanding

    # 7️⃣ Risk-adjusted valuation change
    risk_adjusted_ev_change = enterprise_value_change * (confidence_level / 100)

    # 8️⃣ Impact magnitude metric (Peter-style)
    impact_magnitude = enterprise_value_change / max(confidence_level, 1)

    return {
        "revenue_change": revenue_change,
        "ebitda_change": ebitda_change,
        "fcf_change": fcf_change,
        "enterprise_value_change": enterprise_value_change,
        "equity_value_change": equity_value_change,
        "price_impact_per_share": price_impact,
        "risk_adjusted_ev_change": risk_adjusted_ev_change,
        "impact_magnitude": impact_magnitude,
        "calibration_confidence": confidence_level
    }
