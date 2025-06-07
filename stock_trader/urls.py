# stock_trader/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Import Django's auth views
from trading.views import home_view, logout_view, buy_stock, sell_stock, reset_account, transaction_history_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
    path('buy/', buy_stock, name='buy_stock'),
    path('sell/', sell_stock, name='sell_stock'),
    path('reset_account/', reset_account, name='reset_account'),
    path('history/', transaction_history_view, name='transaction_history'),
    # Add other URLs as you create views
]
