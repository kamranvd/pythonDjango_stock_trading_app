# trading/api_utils.py
import requests
from datetime import datetime
from django.conf import settings
from decimal import Decimal

def fetch_daily_historical_data(symbol):
    """Fetches daily historical data from Alpha Vantage."""
    api_key = settings.ALPHA_VANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"Error fetching data for {symbol}: {data.get('Note') or data.get('Error Message')}")
        return None
    
    time_series_key = None
    for key in data.keys():
        if "Time Series" in key and "(Daily)" in key: # Make sure this is robust
            time_series_key = key
            break

    if not time_series_key or time_series_key not in data:
        print(f"DEBUG: 'Time Series (Daily)' key not found in response for {symbol}. Full API Response: {data}")
        return None

    historical_data = []
    for date_str, values in data[time_series_key].items():
        try:
            historical_data.append({
                'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                'open_price': Decimal(values['1. open']),
                'high_price': Decimal(values['2. high']),
                'low_price': Decimal(values['3. low']),
                'close_price': Decimal(values['4. close']),
                'volume': int(values['5. volume']),
            })
        except KeyError as e:
            # This means a *specific sub-key* like '1. open' was missing for a date
            print(f"Missing expected key '{e}' for {symbol} on {date_str}. Skipping this data point.")
            continue
        except Exception as e:
            print(f"Error processing data for {symbol} on {date_str}: {e}")
            continue
    return historical_data

def fetch_current_price(symbol):
    """Fetches the latest available daily close price from Alpha Vantage."""
    api_key = settings.ALPHA_VANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"Error fetching current price for {symbol}: {data.get('Note') or data.get('Error Message')}")
        return None

    time_series_key = None
    for key in data.keys():
        if "Time Series" in key and "(Daily)" in key: # Make sure this is robust
            time_series_key = key
            break

    if not time_series_key or time_series_key not in data:
        print(f"DEBUG: 'Time Series (Daily)' key not found in response for {symbol}. Full API Response: {data}")
        return None

    latest_date = sorted(data[time_series_key].keys(), reverse=True)[0]
    return Decimal(data[time_series_key][latest_date]['4. close'])

