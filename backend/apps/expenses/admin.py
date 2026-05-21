"""
Admin configuration for expense management models.
"""
from django.contrib import admin
from .models import ExpenseCategory, Income, Expense, Saving, Budget


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'created_at')
    search_fields = ('name',)


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'source', 'date', 'created_at')
    list_filter = ('user', 'source', 'date')
    search_fields = ('user__username', 'source')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date', 'description')
    list_filter = ('user', 'category', 'date')
    search_fields = ('user__username', 'description')


@admin.register(Saving)
class SavingAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'goal', 'date')
    list_filter = ('user', 'goal', 'date')
    search_fields = ('user__username', 'goal')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'limit', 'month', 'year')
    list_filter = ('user', 'category', 'month', 'year')
