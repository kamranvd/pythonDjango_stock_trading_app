# trading/admin.py
from django.contrib import admin
from .models import UserProfile, Stock

admin.site.register(UserProfile)
admin.site.register(Stock)

