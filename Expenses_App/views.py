from django.shortcuts import render, redirect,get_object_or_404
from django.db import models
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

#For pdf conversion
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import Income, Expense, ExpenseCategory, Saving, Budget
from .forms import IncomeForm, ExpenseForm, SavingForm, BudgetForm
from django.db.models import Sum


from datetime import datetime
from datetime import date
import calendar

def welcome(request):
    return render(request, 'welcome.html')
@login_required
def home_page(request):
    return render(request, 'home.html')

def login_page(request):
    if request.method == 'POST':
        username=request.POST.get('uusername')
        password=request.POST.get('upassword')

        if  User.objects.filter(username=username,password=password).exists():
            messages.error(request,'User Already exists')
            return redirect('login')
        else:
            user=authenticate(request,username=username,password=password)
            # print(user)
            if user is None:
                messages.error(request,'Invalid Credentials')
                return redirect('login')
            else:
                login(request,user)
                return redirect('home')


    return render(request, 'login.html')

def register_page(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        lastname=request.POST.get('lname')
        confirm_password=request.POST.get('confirm_password')
        email = request.POST.get('email')

        if password != confirm_password:
            messages.info(request, 'Password does not match to confirm password')
            return redirect('register')

        user_exist = User.objects.filter(username=username)
        if user_exist.exists():
            messages.info(request, 'Username or Email Already Exists')
            return redirect('register')

        user_data = User.objects.create(
            first_name=name,
            username=username,
            email=email,
            last_name=lastname,

        )
        user_data.set_password(password)


        user_data.save()
        messages.info(request, 'Account Created Successfully Go To Login Page')

        return redirect('register')

    return render(request, 'register.html')


def logout_page(request):
    logout(request)
    return redirect('welcome')


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, exp_id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('expenses')

@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, income_id=income_id, user=request.user)
    income.delete()
    messages.success(request, 'Income deleted successfully.')
    return redirect('income')

@login_required
def delete_saving(request, saving_id):
    saving = get_object_or_404(Saving, id=saving_id, user=request.user)
    saving.delete()
    messages.success(request, 'Saving deleted successfully.')
    return redirect('savings')

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully.')
    return redirect('budget')




@login_required
def income(request):
    user = request.user
    income = Income.objects.filter(user=user).first()
    income_form = IncomeForm(instance=income)



    if request.method == 'POST':
        income_form = IncomeForm(request.POST, instance=income)
        if income_form.is_valid():

            income = income_form.save(commit=False)
            income.user = user
            if income.amount<0:
                messages.error(request, 'Income amount cannot be negative.')
                return redirect('income')
            else:
                income.save()
                messages.success(request, 'Income updated successfully.')
                return redirect('income')

        else:
            messages.error(request, 'Invalid income data. Please correct the errors.')

    context = {'income_form': income_form, 'income': income}
    return render(request, 'income.html', context)

@login_required
def expense_view(request):

    user = request.user
    expenses = Expense.objects.filter(user=user).order_by('-date')
    expense_categories = ExpenseCategory.objects.all()
    expense_form = ExpenseForm()
    budgets = Budget.objects.filter(user=user)

    exp = Expense.objects.filter(user=user)
    total_expenses = exp.aggregate(Sum('amount'))['amount__sum'] or 0

    search_date = request.GET.get('search_date')
    search_category = request.GET.get('search_category')
    search_month = request.GET.get('search_month')

    if search_date:
        expenses = expenses.filter(date=search_date)
    if search_category:
        expenses = expenses.filter(category_id=search_category)

    if search_month:
        try:
            if search_month:
                year_str, month_str = search_month.split('-')
                year = int(year_str)
                month = int(month_str)
                _, num_days = calendar.monthrange(year, month)
                start_date = datetime(year, month, 1).date()
                end_date = datetime(year, month, num_days).date()
                expenses = expenses.filter(date__gte=start_date, date__lte=end_date)
        except ValueError:
            messages.error(request, 'Invalid month format. Please use YYYY-MM.')

    if request.method == 'POST':
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            expense = expense_form.save(commit=False)
            expense.user = user

            if expense.amount < 0:
                messages.error(request, 'Expense amount cannot be negative.')
                return redirect('expenses')

            # Budget check.
            budget = budgets.filter(category=expense.category).first()
            if budget:
                category_expenses = \
                Expense.objects.filter(user=user, category=expense.category).aggregate(Sum('amount'))[
                    'amount__sum'] or 0
                if (category_expenses + expense.amount) > budget.limit:
                    messages.error(request, f'Expense exceeds budget limit for {expense.category.name}.')
                    return redirect('expenses')

            expense.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('expenses')
        else:
            messages.error(request, 'Invalid expense data. Please correct the errors.')

    context = {
        'expense_form': expense_form,
        'expenses': expenses,
        'expense_categories': expense_categories,
        'search_date': search_date,
        'search_month': search_month,
        'search_category': search_category,
        'total_expenses': total_expenses
    }
    return render(request, 'expenses.html', context)


@login_required
def budget_view(request):
    user = request.user
    budgets = Budget.objects.filter(user=user)
    budget_form = BudgetForm()
    # category=ExpenseCategory.objects.all()

    categories_with_budget = budgets.values_list('category', flat=True)
    all_categories = ExpenseCategory.objects.all()

    if request.method == 'POST':
        budget_form = BudgetForm(request.POST)
        if budget_form.is_valid():
            category = budget_form.cleaned_data['category']
            if category.id in categories_with_budget:
                messages.info(request, f'A budget limit is already set for the category')
                return redirect('budget')

            else:
                budget = budget_form.save(commit=False)
                budget.user = user

                if budget.limit < 0:
                    messages.error(request, 'Budget limit cannot be negative.')
                    return redirect('budget')
                else:
                    budget.save()
                    messages.success(request, 'Budget added successfully.')
                    return redirect('budget')

        else:
            messages.error(request, 'Invalid budget data. Please correct the errors.')
    context = {'budget_form': budget_form, 'budgets': budgets}
    return render(request, 'budget.html', context)

@login_required
def saving_view(request):
    user = request.user
    savings = Saving.objects.filter(user=user).order_by('-date')
    saving_form = SavingForm()
    # saving_=Saving.objects.filter(user=user).first()
    income = Income.objects.filter(user=user).first()
    expenses = Expense.objects.filter(user=user)
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_amount = (income.amount - total_expenses) if income else 0
    saving_amt=Saving.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    saving_amount=remaining_amount-saving_amt

    if request.method == 'POST':
        saving_form = SavingForm(request.POST)
        if saving_form.is_valid():

            saving = saving_form.save(commit=False)
            saving.user = user
            if saving.amount < 0:
                messages.error(request, 'Saving amount cannot be negative.')
                return redirect('savings')

            # Check if saving amount is valid
            elif saving.amount > remaining_amount:
                messages.error(request, 'Saving amount exceeds remaining amount.')
                return redirect('savings')

            saving.save()
            messages.success(request, 'Saving added successfully.')
            # save=remaining_amount-saving.amount
            return redirect('savings')
        else:
            messages.error(request, 'Invalid saving data. Please correct the errors.')

    context = {'saving_form': saving_form, 'savings': savings, 'saving_amount': saving_amount,}
    return render(request, 'savings.html', context)


@login_required
def generate_expense_pdf(request):
    user = request.user
    search_month_year = request.POST.get('search_month')  # Get the month from the POST request

    if not search_month_year:
        return HttpResponse("Please select a month to generate the PDF.")

    try:
        year_str, month_str = search_month_year.split('-')
        year = int(year_str)
        month = int(month_str)
        _, num_days = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, num_days).date()
        expenses = Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date).order_by('-date')
    except (ValueError, IndexError):
        return HttpResponse("Invalid month format. Please use YYYY-MM.")

    inc = Income.objects.filter(user=user).first()  # Consider filtering Income by month/year if needed
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_amount = (inc.amount - total_expenses) if inc else 0

    template_path = 'expenses/expense_pdf.html'
    context = {
        'expenses': expenses,
        'user': user,
        'total_expenses': total_expenses,
        'remaining_amount': remaining_amount,
        'month_name': calendar.month_name[month],
        'year': year,
    }
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="expenses_{calendar.month_name[month]}_{year}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response




def about_us(request):
    return render(request, 'AboutUs/aboutus.html')

def chatbot_view(request):
    return render(request, 'Chatbot/chatbot.html')