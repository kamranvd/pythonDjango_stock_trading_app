from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .models import UserProfile, Stock, HistoricalPrice, Holding, Transaction
from django.db import transaction as db_transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal

@login_required
def home_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    # For simplicity, we'll pass some initial data.
    # This will be refined significantly.
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
    stock_symbol = request.POST.get('symbol')
    quantity = int(request.POST.get('quantity'))
    current_price = Decimal(request.POST.get('price')) # Get from frontend for now, but later get from API

    stock = get_object_or_404(Stock, symbol=stock_symbol)

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
                price=current_price
            )
        return JsonResponse({'success': True, 'message': 'Stock bought successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Transaction failed: {str(e)}'}, status=500)

@login_required
@require_POST
def sell_stock(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    stock_symbol = request.POST.get('symbol')
    quantity = int(request.POST.get('quantity'))
    current_price = Decimal(request.POST.get('price')) # Get from frontend for now, but later get from API

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
                holding.delete() # Remove holding if quantity is zero
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
    return redirect('home') # Redirect to home or a confirmation page

@login_required
def transaction_history_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    transactions = Transaction.objects.filter(user_profile=user_profile).order_by('-transaction_date')

    # Logic for portfolio value fluctuation chart will go here
    # This is more complex and will involve calculating portfolio value daily
    # based on historical prices and holdings.

    context = {
        'transactions': transactions,
        # 'portfolio_value_data': ... (for chart)
    }
    return render(request, 'trading/transaction_history.html', context)


def logout_view(request):
    auth_logout(request)
    return redirect('login') # Redirect to login page
