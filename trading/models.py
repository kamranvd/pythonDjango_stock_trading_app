# trading/models.py
from django.db import models
from django.contrib.auth.models import User # Use Django's built-in User model

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00) # Initial cash

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def reset_account(self):
        """Resets cash and deletes all transactions and holdings."""
        self.cash_balance = 10000.00 # Or whatever your initial balance is
        self.save()
        Transaction.objects.filter(user_profile=self).delete()
        Holding.objects.filter(user_profile=self).delete()


class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    # You might want to add more static stock info here

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class HistoricalPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'date') # Ensure no duplicate prices for a stock on a given day
        ordering = ['date']

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}: {self.close_price}"

class Holding(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user_profile', 'stock') # Each user holds a stock once

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.stock.symbol}: {self.quantity}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at time of transaction
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile.user.username} {self.transaction_type} {self.quantity} of {self.stock.symbol} at {self.price}"

