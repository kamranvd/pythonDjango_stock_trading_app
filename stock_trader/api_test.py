import requests
import json # Import json to pretty-print the data
from django.conf import settings # If you're loading from settings

api_key = settings.ALPHA_VANTAGE_API_KEY # Make sure settings is configured for this

symbol = 'IBM'
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={api_key}"

print(f"Requesting URL: {url}")
response = requests.get(url)
data = response.json()

# <<< CAREFULLY INSPECT THIS OUTPUT >>>
print(json.dumps(data, indent=2)) # This will pretty-print the JSON

# Now, try to access the keys you expect
# What are the top-level keys?
print("\nTop-level keys in response:")
for key in data.keys():
    print(f"- {key}")

# Check for the expected "Time Series" key
time_series_key = None
for key in data.keys():
    if "Time Series" in key:
        time_series_key = key
        break

if time_series_key:
    print(f"\nFound time series data under key: '{time_series_key}'")
    first_date_data = data[time_series_key][sorted(data[time_series_key].keys(), reverse=True)[0]]
    print(f"Data for latest date: {first_date_data}")
    print(f"Close price key name: {first_date_data.keys()}")
else:
    print("\n'Time Series' key not found in the response! This is the problem.")