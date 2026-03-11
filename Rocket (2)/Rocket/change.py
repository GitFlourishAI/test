import numpy, pandas
from dataclasses import dataclass, asdict

from pandas._libs.tslibs import timestamps
from psycopg2 import Timestamp
from pydantic_core.core_schema import DateSchema
from alpha import AlphaVantageClient
import os
from datetime import datetime

client = AlphaVantageClient()
data = client.get_FX_Monthly()

@dataclass
class Change:
    data_type: str
    current_exchange_rate: float
    exchange_rate_last_month: float
    change_pct: float
    revenue_change: float
    cost_change: float
    is_significant: bool
    mechanism: str
    time: str


class FXAnomalyDetector:

  def __init__(self, change_pct:float = 0.01):
       self.change_pct = change_pct

  def detect_anomalies(self, data: dict) -> list[Change]:

      time_series = data.get("Time Series FX (Monthly)", {})

      if not time_series:
          return []

      sorted_dates = sorted(time_series, reverse=True)

      current_exchange_rate = float(time_series[sorted_dates[0]]["4. close"])

      exchange_rate_last_month = float(time_series[sorted_dates[1]]["4. close"])

      change_pct = (current_exchange_rate - exchange_rate_last_month) / exchange_rate_last_month

      revenue_change = 0.6* change_pct
      cost_change = 0.4* change_pct
      is_significant = abs(change_pct) > self.change_pct

      if change_pct > 0:

          mechanism = "CNY appreciation"

      else:
        
          mechanism = "CNY depreciation"


      return [Change(
           data_type="fx_monthly",
           current_exchange_rate=current_exchange_rate,
           exchange_rate_last_month=exchange_rate_last_month,
           change_pct=change_pct,
           revenue_change=revenue_change,
           cost_change=cost_change,
           mechanism = mechanism,
           is_significant=is_significant,
           time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
           )]



detector = FXAnomalyDetector(change_pct=0.01)

anomalies = detector.detect_anomalies(data)

for anomaly in anomalies:
         print(f"Anomaly detected:{anomaly.change_pct}, is_significant: {anomaly.is_significant}, current_exchange_rate: {anomaly.current_exchange_rate}, exchange_rate_last_month: {anomaly.exchange_rate_last_month}, mechanism: {anomaly.mechanism}, time: {anomaly.time}, revenue_change: {anomaly.revenue_change}, cost_change: {anomaly.cost_change}, data_type: {anomaly.data_type}")