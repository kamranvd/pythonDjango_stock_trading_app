from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .models import UserProfile, Stock, HistoricalPrice, Holding, Transaction
from django.db import transaction as db_transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from .api_utils import fetch_daily_historical_data, fetch_current_price
import json

@login_required
def home_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    stocks = Stock.objects.all()
    portfolio_holdings = Holding.objects.filter(user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'stocks': stocks,
        'portfolio_holdings': portfolio_holdings,
        'cash_balance': user_profile.cash_balance,
    }
    return render(request, 'trading/home.html', context)

@login_required
@require_POST
def buy_stock(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    stock_symbol = request.POST.get('symbol').upper()
    quantity = int(request.POST.get('quantity'))
    stock = get_object_or_404(Stock, symbol=stock_symbol)
    current_price = fetch_current_price(stock.symbol) # **Get actual current price**
    
    if current_price is None:
        return JsonResponse({'success': False, 'message': 'Could not fetch current price for trading.'}, status=500)
    total_cost = quantity * current_price
    if user_profile.cash_balance < total_cost:
        return JsonResponse({'success': False, 'message': 'Insufficient funds.'}, status=400)
    try:
        with db_transaction.atomic():
            user_profile.cash_balance -= total_cost
            user_profile.save()
            holding, created = Holding.objects.get_or_create(
                user_profile=user_profile,
                stock=stock,
                defaults={'quantity': 0}
            )
            holding.quantity += quantity
            holding.save()
            Transaction.objects.create(
                user_profile=user_profile,
                stock=stock,
                transaction_type='BUY',
                quantity=quantity,
                price=current_price # Record the actual price
            )
        return JsonResponse({'success': True, 'message': 'Stock bought successfully.', 'new_cash_balance': float(user_profile.cash_balance)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Transaction failed: {str(e)}'}, status=500)


@login_required
@require_POST
def sell_stock(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    stock_symbol = request.POST.get('symbol')
    quantity = int(request.POST.get('quantity'))
    current_price = Decimal(request.POST.get('price')) 

    stock = get_object_or_404(Stock, symbol=stock_symbol)
    holding = get_object_or_404(Holding, user_profile=user_profile, stock=stock)

    if holding.quantity < quantity:
        return JsonResponse({'success': False, 'message': 'Insufficient shares to sell.'}, status=400)

    total_revenue = quantity * current_price

    try:
        with db_transaction.atomic():
            user_profile.cash_balance += total_revenue
            user_profile.save()

            holding.quantity -= quantity
            if holding.quantity == 0:
                holding.delete() 
            else:
                holding.save()

            Transaction.objects.create(
                user_profile=user_profile,
                stock=stock,
                transaction_type='SELL',
                quantity=quantity,
                price=current_price
            )
        return JsonResponse({'success': True, 'message': 'Stock sold successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Transaction failed: {str(e)}'}, status=500)


@login_required
def reset_account(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_profile.reset_account()
    return redirect('home') 

@login_required
def transaction_history_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    transactions = Transaction.objects.filter(user_profile=user_profile).order_by('-transaction_date')

    for transaction in transactions:
        transaction.total_amount = transaction.quantity * transaction.price


    context = {
        'transactions': transactions,
    }
    return render(request, 'trading/transaction_history.html', context)

@login_required
def get_stock_details(request, symbol):
    """API endpoint to get current price and historical data for a stock."""
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    current_price = fetch_current_price(stock.symbol)
    if current_price is None:
        return JsonResponse({'error': 'Could not fetch current price.'}, status=500)

    latest_db_date = HistoricalPrice.objects.filter(stock=stock).order_by('-date').first()
    today = datetime.now().date()
    if not latest_db_date or (today - latest_db_date.date).days > 0: # Fetch if no data or data is old
        historical_api_data = fetch_daily_historical_data(stock.symbol)
        if historical_api_data:
            # Save new historical data to DB
            for data_point in historical_api_data:
                # Use update_or_create to avoid duplicates on re-fetching
                HistoricalPrice.objects.update_or_create(
                    stock=stock,
                    date=data_point['date'],
                    defaults={
                        'open_price': data_point['open_price'],
                        'high_price': data_point['high_price'],
                        'low_price': data_point['low_price'],
                        'close_price': data_point['close_price'],
                        'volume': data_point['volume'],
                    }
                )
            print(f"Fetched and saved new historical data for {stock.symbol}")
        else:
            print(f"Failed to fetch historical data for {stock.symbol}")
    historical_prices = HistoricalPrice.objects.filter(stock=stock).order_by('date')
    chart_data = {
        'labels': [p.date.strftime('%Y-%m-%d') for p in historical_prices],
        'close_prices': [float(p.close_price) for p in historical_prices],
    }
    return JsonResponse({
        'symbol': stock.symbol,
        'name': stock.name,
        'current_price': float(current_price),
        'historical_data': chart_data
    })

def logout_view(request):
    auth_logout(request)
    return redirect('login')
