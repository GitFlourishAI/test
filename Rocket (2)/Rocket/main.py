import schedule
from datetime import datetime, time, timedelta
from change import anomalies, FXAnomalyDetector
from alpha import AlphaVantageClient
import time as tm
from signal123 import save_event, SQL, save_catalysts
from test import revisedCatalystList, think_then_answer_then_reflect, CatalystReport
import asyncio
from typing import List    



def workflow():
    # Get data from database and format it as a string
    raw_data = SQL()

    if raw_data:
        user_input = f"""
        Event Data:
        - Data Type: {raw_data[0]}
        - Price Today: {raw_data[1]}
        - Price Yesterday: {raw_data[2]}
        - Change Percentage: {raw_data[3]}
        - Is Significant: {raw_data[4]}
        - Direction: {raw_data[5]}
        - Time: {raw_data[6]}
        """
    else:
        print("No data available")
        return

    # Run the async function
    result: List[revisedCatalystList] = asyncio.run(think_then_answer_then_reflect(user_input))
    
    for r in result: 
        save_catalysts(r.id, r.title, r.description, r.sector_id, r.source_type, r.source_name, r.source_url, r.detected_at, r.time_horizon, r.confidence_score, r.impact_magnitude, r.impact_direction, r.status, r.shock_type, r.evidence_summary, r.ticker, r.revenue_impact, r.ebitda_impact, r.valuation_delta)

schedule.every(1).minutes.do(workflow)

while True:

    schedule.run_pending()

    tm.sleep(10)