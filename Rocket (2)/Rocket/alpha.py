import os
import requests
import pandas

def get_alpha():

  return os.environ.get("ALPHA_VANTAGE_API_KEY")

get_alpha()

BASE_URL = "https://www.alphavantage.co/query"

class AlphaVantageClient:

    def __init__(self, api_key: str | None = None):
      if api_key is None:
          api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
      if api_key is None:
          raise ValueError("API key not provided")
      self.api_key = api_key

    def _make_request(self, params):

        return  requests.get(BASE_URL, params=params)

    def get_intraday_data(self, symbol: str, interval: str = "5min", output_size: str = "compact"):
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": output_size,
            "apikey": self.api_key
        }
        response = self._make_request(params)
        response.raise_for_status()

        return response.json()

    def get_treasury_yield(self, interval: str = "monthly", maturity: str = "10year"):

        params = {
            "function": "TREASURY_YIELD",
            "interval": interval,
            "maturity": maturity,
            "apikey": self.api_key
        }
        response = self._make_request(params)

        return response.json()

    def get_FX_Monthly(self, from_symbol: str = "CNY", to_symbol: str = "USD", outputsize: str = "compact"):
        params = {
            "function": "FX_MONTHLY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        response = self._make_request(params)
        return response.json()

    def get_INCOME_STATEMENT(self, symbol:str):
    
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol,

            "apikey": self.api_key
    }
        response = self._make_request(params)
        return response.json()






if __name__ == "__main__":
    client = AlphaVantageClient(get_alpha())
    data = client.get_FX_Monthly()
    print(data)

