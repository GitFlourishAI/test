import schedule
from datetime import datetime, time, timedelta
from change import anomalies, FXAnomalyDetector
from alpha import AlphaVantageClient
import time as tm
from signal123 import save_event

def job():

   client = AlphaVantageClient()
   data = client.get_FX_Monthly()

   detector = FXAnomalyDetector(change_pct= 0.01)

   result = detector.detect_anomalies(data)

   for anomaly in result:
        
        print(f"Anomaly detected:{anomaly.change_pct}")
        save_event(anomaly.data_type, anomaly.current_exchange_rate, anomaly.exchange_rate_last_month, anomaly.change_pct, anomaly.revenue_change, anomaly.cost_change, anomaly.mechanism, anomaly.is_significant, anomaly.time)

schedule.every(5).seconds.do(job)

while True:

   schedule.run_pending()
   tm.sleep(5)
