import os
import pandas as pd
from financetoolkit import Toolkit

pd.set_option("display.max_columns", 12)
pd.set_option("display.width", 120)

API_KEY = os.environ.get("FMP_API_KEY", "")

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN"]
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"


def print_section(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def main():
    print_section("FinanceToolkit - Fundamental Analysis Demo")

    if not API_KEY:
        print("ERROR: FMP_API_KEY environment variable is not set.")
        print("Please add your Financial Modeling Prep API key to Secrets.")
        return

    print(f"Tickers: {', '.join(TICKERS)}")
    print(f"Period:  {START_DATE} to {END_DATE}")
    print(f"API Key: {'*' * 8}...{API_KEY[-4:]}")

    print("\nInitializing Toolkit...")
    toolkit = Toolkit(
        tickers=TICKERS,
        api_key=API_KEY,
        start_date=START_DATE,
        end_date=END_DATE,
    )
    print("Toolkit ready.")

    print_section("1. Income Statement")
    try:
        income = toolkit.get_income_statement()
        key_rows = ["Revenue", "Cost of Goods Sold", "Gross Profit",
                     "Operating Income", "Net Income"]
        idx = income.index.get_level_values(1).isin(key_rows)
        print(income.loc[idx])
    except Exception as e:
        print(f"Could not retrieve income statement: {e}")

    print_section("2. Balance Sheet Statement")
    try:
        balance = toolkit.get_balance_sheet_statement()
        key_rows = ["Total Assets", "Total Liabilities", "Total Equity",
                     "Total Current Assets", "Total Current Liabilities"]
        idx = balance.index.get_level_values(1).isin(key_rows)
        print(balance.loc[idx])
    except Exception as e:
        print(f"Could not retrieve balance sheet: {e}")

    print_section("3. Cash Flow Statement")
    try:
        cash = toolkit.get_cash_flow_statement()
        key_rows = ["Operating Cash Flow", "Capital Expenditure",
                     "Free Cash Flow", "Dividends Paid"]
        idx = cash.index.get_level_values(1).isin(key_rows)
        print(cash.loc[idx])
    except Exception as e:
        print(f"Could not retrieve cash flow statement: {e}")

    print_section("4. Profitability Ratios")
    try:
        profitability = toolkit.ratios.collect_profitability_ratios()
        print(profitability)
    except Exception as e:
        print(f"Could not compute profitability ratios: {e}")

    print_section("5. Liquidity Ratios")
    try:
        liquidity = toolkit.ratios.collect_liquidity_ratios()
        print(liquidity)
    except Exception as e:
        print(f"Could not compute liquidity ratios: {e}")

    print_section("6. Solvency Ratios")
    try:
        solvency = toolkit.ratios.collect_solvency_ratios()
        print(solvency)
    except Exception as e:
        print(f"Could not compute solvency ratios: {e}")

    print_section("7. Efficiency Ratios")
    try:
        efficiency = toolkit.ratios.collect_efficiency_ratios()
        print(efficiency)
    except Exception as e:
        print(f"Could not compute efficiency ratios: {e}")

    print_section("8. Valuation Ratios")
    try:
        valuation = toolkit.ratios.collect_valuation_ratios()
        print(valuation)
    except Exception as e:
        print(f"Could not compute valuation ratios: {e}")

    print_section("9. Dupont Analysis")
    try:
        dupont = toolkit.models.get_extended_dupont_analysis()
        print(dupont)
    except Exception as e:
        print(f"Could not compute Dupont analysis: {e}")

    print_section("10. Altman Z-Score")
    try:
        altman = toolkit.models.get_altman_z_score()
        print(altman)
    except Exception as e:
        print(f"Could not compute Altman Z-Score: {e}")

    print_section("11. Piotroski F-Score")
    try:
        piotroski = toolkit.models.get_piotroski_score()
        print(piotroski)
    except Exception as e:
        print(f"Could not compute Piotroski F-Score: {e}")


    print_section("12. Segment Revenue")
    try:
        segment_revenue = toolkit.get_revenue_geographic_segmentation()
        print(segment_revenue)
    except Exception as e:
        print(f"Could not retrieve segment revenue: {e}")

    print_section("Done!")
    print("Fundamental analysis complete for", ", ".join(TICKERS))
    print()
    print("You can customize this script by changing TICKERS, START_DATE,")
    print("and END_DATE at the top of main.py.")
    print()
    print("For more features, explore the examples/ directory.")


if __name__ == "__main__":
    main()
