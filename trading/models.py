# trading/models.py
from django.db import models
from django.contrib.auth.models import User 

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00) # Initial cash

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def reset_account(self):
        """Resets cash and deletes all transactions and holdings."""
        self.cash_balance = 10000.00 # initial balance 
        self.save()
        Transaction.objects.filter(user_profile=self).delete()
        Holding.objects.filter(user_profile=self).delete()


class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

