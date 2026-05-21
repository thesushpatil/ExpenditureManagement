"""
Models for the expense management system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal


class ExpenseCategory(models.Model):
    """Categories for organizing expenses (e.g., Food, Transport, Entertainment)."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, default='receipt')
    color = models.CharField(max_length=7, blank=True, default='#6366f1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Income(models.Model):
    """User income records."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    source = models.CharField(max_length=100, blank=True, default='Salary')
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.source}: {self.amount}"


class Expense(models.Model):
    """User expense records."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.category.name}: {self.amount}"


class Saving(models.Model):
    """User savings records."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings')
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    goal = models.CharField(max_length=100, blank=True, default='General')
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.goal}: {self.amount}"


class Budget(models.Model):
    """Monthly budget limits per category."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='budgets')
    limit = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    month = models.PositiveIntegerField(help_text='Month (1-12)')
    year = models.PositiveIntegerField(help_text='Year (e.g., 2025)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.user.username} - {self.category.name}: {self.limit} ({self.month}/{self.year})"


# ===== KHATABOOK (Ledger) MODULE =====

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message='Enter a valid phone number (7-15 digits, optional + prefix).'
)


class Contact(models.Model):
    """A person you lend money to or borrow money from (like Khatabook contacts)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=16, validators=[phone_validator])
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'phone')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone})"


class LedgerEntry(models.Model):
    """
    A transaction entry in the ledger (Khatabook style).
    - type='gave' means YOU gave money to the contact (they owe you)
    - type='got' means YOU got money from the contact (you owe them less / they paid back)
    """
    TRANSACTION_TYPES = [
        ('gave', 'You Gave'),   # You lent money - they owe you
        ('got', 'You Got'),     # They paid you back / you borrowed and they gave
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ledger_entries')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='entries')
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    notify_sent = models.BooleanField(default=False, help_text='Whether SMS/WhatsApp reminder was sent')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Ledger Entries'

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} ₹{self.amount} {'to' if self.transaction_type == 'gave' else 'from'} {self.contact.name}"
