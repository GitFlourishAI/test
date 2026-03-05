import schedule
from datetime import datetime, time, timedelta
from change import anomalies, FXAnomalyDetector
from alpha import AlphaVantageClient
import time as tm
from signal123 import save_event, SQL, save_catalysts
from test import think_then_answer_then_reflect, CatalystReport
import asyncio


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
    result = asyncio.run(think_then_answer_then_reflect(user_input))

    print(result)
    save_catalysts(result.id, result.title, result.description, result.sector_id, result.source_type, result.source_name, result.source_url, result.detected_at, result.time_horizon, result.confidence_score, result.impact_magnitude, result.impact_direction, result.status, result.shock_type, result.evidence_summary)

schedule.every(1).minutes.do(workflow)

while True:

    schedule.run_pending()

    tm.sleep(10)