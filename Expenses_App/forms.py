from django import forms
from .models import Income, Expense, Saving, Budget, ExpenseCategory

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'description']

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name']

class SavingForm(forms.ModelForm):
    class Meta:
        model = Saving
        fields = ['amount', 'description']

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit', ]