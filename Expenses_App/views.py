from django.shortcuts import render, redirect,get_object_or_404
from django.db import models
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required



from .models import Income, Expense, ExpenseCategory, Saving, Budget
from .forms import IncomeForm, ExpenseForm, SavingForm, BudgetForm
from django.db.models import Sum


from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def home(request):
    return render(request, 'home_page.html')

def login_page(request):
    if request.method == 'POST':
        username=request.POST.get('uusername')
        password=request.POST.get('upassword')

        if  User.objects.filter(username=username,password=password).exists():
            messages.error(request,'User Already exists')
            return redirect('login')
        else:
            user=authenticate(request,username=username,password=password)
            print(user)
            if user is None:
                messages.error(request,'The User Does Not Exist')
                return redirect('login')
            else:
                login(request,user)
                return redirect('expense_manager')



    return render(request, 'login.html')

def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')

        user_exist = User.objects.filter(username=username)
        if user_exist.exists():
            messages.info(request, 'Username or Email Already Exists')
            return redirect('register')

        user_data = User.objects.create(
            username=username,
            first_name=fname,
            last_name=lname,
            email=email
        )
        user_data.set_password(password)
        user_data.save()
        messages.info(request, 'Account Created Successfully Go To Login Page')

        return redirect('register')

    return render(request, 'register.html')


def logout_page(request):
    logout(request)
    return redirect('login')



@login_required
def expense_manager(request):
    user = request.user
    income = Income.objects.filter(user=user).first()
    expenses = Expense.objects.filter(user=user).order_by('-date')
    expense_categories = ExpenseCategory.objects.all()
    savings = Saving.objects.filter(user=user).order_by('-date')
    budgets = Budget.objects.filter(user=user)

    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_amount = income.amount - total_expenses if income else 0

    income_form = IncomeForm(instance=income)
    expense_form = ExpenseForm()
    saving_form = SavingForm()
    budget_form = BudgetForm()
    # category_form = ExpenseCategoryForm()

    if request.method == 'POST':
        if 'income_submit' in request.POST:
            income_form = IncomeForm(request.POST, instance=income)
            if income_form.is_valid():
                income = income_form.save(commit=False)
                income.user = user
                income.save()
                messages.success(request, 'Income updated successfully.')
                return redirect('expense_manager')
            else:
                messages.error(request, 'Invalid income data. Please correct the errors.')

        elif 'expense_submit' in request.POST:
            expense_form = ExpenseForm(request.POST)
            if expense_form.is_valid():
                expense = expense_form.save(commit=False)
                expense.user = user

                # Budget check.
                budget = Budget.objects.filter(user=user, category=expense.category).first()
                if budget:
                    category_expenses = Expense.objects.filter(user=user, category=expense.category).aggregate(Sum('amount'))['amount__sum'] or 0
                    if (category_expenses + expense.amount) > budget.limit:
                        messages.error(request, f'Expense exceeds budget limit for {expense.category.name}.')
                        return redirect('expense_manager')

                expense.save()
                messages.success(request, 'Expense added successfully.')
                return redirect('expense_manager')
            else:
                messages.error(request, 'Invalid expense data. Please correct the errors.')

        elif 'saving_submit' in request.POST:
            saving_form = SavingForm(request.POST)
            if saving_form.is_valid():
                saving = saving_form.save(commit=False)
                saving.user = user

                # Check if saving amount is valid
                if saving.amount > remaining_amount:
                    messages.error(request, 'Saving amount exceeds remaining amount.')
                    return redirect('expense_manager')

                saving.save()
                messages.success(request, 'Saving added successfully.')

                # Recalculate remaining amount after saving
                remaining_amount = remaining_amount - saving.amount

                # Update the remaining amount in the context.
                context = {
                    'income': income,
                    'expenses': expenses,
                    'expense_categories': expense_categories,
                    'savings': savings,
                    'budgets': budgets,
                    'total_expenses': total_expenses,
                    'remaining_amount': remaining_amount,
                    'income_form': income_form,
                    'expense_form': expense_form,
                    'saving_form': saving_form,
                    'budget_form': budget_form,
                    # 'category_form': category_form,
                }
                return render(request, 'expense_manager.html', context)
            else:
                messages.error(request, 'Invalid saving data. Please correct the errors.')

        elif 'budget_submit' in request.POST:
            budget_form = BudgetForm(request.POST)
            if budget_form.is_valid():
                budget = budget_form.save(commit=False)
                budget.user = user
                budget.save()
                messages.success(request, 'Budget added successfully.')
                return redirect('expense_manager')
            else:
                messages.error(request, 'Invalid budget data. Please correct the errors.')

        # elif 'category_submit' in request.POST:
        #     category_form = ExpenseCategoryForm(request.POST)
        #     if category_form.is_valid():
        #         category_form.save()
        #         messages.success(request, 'Category added successfully.')
        #         return redirect('expense_manager')
        #     else:
        #         messages.error(request, 'Invalid category data. Please correct the errors.')

    context = {
        'income': income,
        'expenses': expenses,
        'expense_categories': expense_categories,
        'savings': savings,
        'budgets': budgets,
        'total_expenses': total_expenses,
        'remaining_amount': remaining_amount,
        'income_form': income_form,
        'expense_form': expense_form,
        'saving_form': saving_form,
        'budget_form': budget_form,
        # 'category_form': category_form,
    }
    return render(request, 'expense_manager.html', context)

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, exp_id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('expense_manager')

@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, income_id=income_id, user=request.user)
    income.delete()
    messages.success(request, 'Income deleted successfully.')
    return redirect('expense_manager')

@login_required
def delete_saving(request, saving_id):
    saving = get_object_or_404(Saving, id=saving_id, user=request.user)
    saving.delete()
    messages.success(request, 'Saving deleted successfully.')
    return redirect('expense_manager')

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully.')
    return redirect('expense_manager')