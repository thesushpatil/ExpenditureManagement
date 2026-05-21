"""
URL patterns for expense management endpoints.

Endpoints:
    GET/POST   /api/v1/categories/           - List/Create categories
    GET/PUT/DELETE /api/v1/categories/{id}/   - Category detail

    GET/POST   /api/v1/incomes/              - List/Create incomes
    GET/PUT/DELETE /api/v1/incomes/{id}/      - Income detail
    GET        /api/v1/incomes/summary/      - Income summary

    GET/POST   /api/v1/expenses/             - List/Create expenses
    GET/PUT/DELETE /api/v1/expenses/{id}/     - Expense detail
    GET        /api/v1/expenses/summary/     - Expense summary
    GET        /api/v1/expenses/by-category/ - Expenses by category

    GET/POST   /api/v1/savings/              - List/Create savings
    GET/PUT/DELETE /api/v1/savings/{id}/      - Saving detail
    GET        /api/v1/savings/summary/      - Savings summary

    GET/POST   /api/v1/budgets/              - List/Create budgets
    GET/PUT/DELETE /api/v1/budgets/{id}/      - Budget detail

    GET        /api/v1/dashboard/            - Dashboard summary
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExpenseCategoryViewSet, IncomeViewSet, ExpenseViewSet,
    SavingViewSet, BudgetViewSet, DashboardView,
    ContactViewSet, LedgerEntryViewSet,
)

router = DefaultRouter()
router.register(r'categories', ExpenseCategoryViewSet, basename='category')
router.register(r'incomes', IncomeViewSet, basename='income')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'savings', SavingViewSet, basename='saving')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'ledger', LedgerEntryViewSet, basename='ledger')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
