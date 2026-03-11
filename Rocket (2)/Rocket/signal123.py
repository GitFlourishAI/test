import os
import psycopg2


def save_event(data_type: str, current_exchange_rate: float, exchange_rate_last_month: float, change_pct: float, revenue_change: float, cost_change: float, mechanism: str, is_significant: bool,  time: str):


         database_url = os.environ['DATABASE_URL']
         conn = psycopg2.connect(database_url)
         cur = conn.cursor()

         cur.execute("Insert into signal_11 (data_type, current_exchange_rate, exchange_rate_last_month, change_pct, revenue_change, cost_change, mechanism, is_significant, time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (data_type, current_exchange_rate, exchange_rate_last_month, change_pct, revenue_change, cost_change, mechanism, is_significant, time))

         conn.commit()
         cur.close()
         conn.close()


def SQL():

    conn = None
    cur = None

    try:

        database_url = os.environ['DATABASE_URL']
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        cur.execute("SELECT * FROM signal_11 ORDER BY time DESC LIMIT 1")
        rows = cur.fetchone()

        return rows

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()



def save_catalysts(id: str, title: str, description: str, sector_id: str, source_type: str, source_name: str, source_url: str, detected_at: str, time_horizon: str, confidence_score: float, impact_magnitude: float, impact_direction: str, status: str, shock_type:str, evidence_summary: str, ticker:str, revenue_impact: float, ebitda_impact:float, valuation_delta: float):


         database_url = os.environ['DATABASE_URL']
         conn = psycopg2.connect(database_url)
         cur = conn.cursor()

         cur.execute("Insert into catalysts (id, title, description, sector_id, source_type, source_name, source_url, detected_at, time_horizon, confidence_score, impact_magnitude, impact_direction, status, shock_type, evidence_summary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, title, description, sector_id, source_type, source_name, source_url, detected_at, time_horizon, confidence_score, impact_magnitude, impact_direction, status, shock_type, evidence_summary))

         cur.execute("Insert into financial_impacts (catalyst_id, position_id, revenue_impact, ebitda_impact, valuation_delta) VALUES (%s, %s, %s, %s, %s)", (id, ticker, revenue_impact, ebitda_impact, valuation_delta))

       
         conn.commit()
         cur.close()
         conn.close()

