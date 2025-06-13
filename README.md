# pythonDjango_stock_trading_app
Stock Trading App

- Overview/description of the project
    - This is a stock trading app. You can search stock symbols and pretend to buy and sell shares.
- Details on how to use it or what functionality is offered
    - It provides a simple interface with two parts:
      - The first part at the top is the Market View.
        - When you enter a stock symbol and click search the app will pull stock data from Alpha Vantage and display the data in a chart.
      - The second part below is Your Portfolio.
        - This displays the stock you bought, the quantity and the price you bought or sold the stock.
    - Click on the Transaction History and you can see historical data related to your purchases and sales.
    - Click the Reset Account to clear the data and start all over again.
- Technologies Used
    - Python 3.11.1
    - Django 5.2.1
    - MySQL Community Edition: 8.0.30 - required for my older machine
    - Alpha Vangate free stock data API
    - HTML, CSS, and Javascript
- Ideas for future improvement (minimum of 3)
    - To see stock data for more than one stock symbol at a time.
    - A way to increase your starting cash balance.
    - The ability to choose between stock data api services.
      - Currently there's a rate limit for the free version.
