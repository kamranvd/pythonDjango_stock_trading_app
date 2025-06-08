# trading/api_utils.py
import requests
from datetime import datetime
from django.conf import settings
from decimal import Decimal

def fetch_daily_historical_data(symbol):
    """Fetches daily historical data from Alpha Vantage."""
    api_key = settings.ALPHA_VANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"Error fetching data for {symbol}: {data.get('Note') or data.get('Error Message')}")
        return None

    historical_data = []
    for date_str, values in data["Time Series (Daily)"].items():
        try:
            historical_data.append({
                'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                'open_price': Decimal(values['1. open']),
                'high_price': Decimal(values['2. high']),
                'low_price': Decimal(values['3. low']),
                'close_price': Decimal(values['4. close']), 
                'volume': int(values['6. volume']),
            })
        except KeyError:
            print(f"Missing data for {symbol} on {date_str}. Skipping.")
            continue
        except Exception as e:
            print(f"Error processing data for {symbol} on {date_str}: {e}")
            continue
    return historical_data

def fetch_current_price(symbol):
    """Fetches the latest available daily close price from Alpha Vantage."""
    api_key = settings.ALPHA_VANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"Error fetching current price for {symbol}: {data.get('Note') or data.get('Error Message')}")
        return None

    # Get the latest date's data
    latest_date = sorted(data["Time Series (Daily)"].keys(), reverse=True)[0]
    return Decimal(data["Time Series (Daily)"][latest_date]['4. close'])

