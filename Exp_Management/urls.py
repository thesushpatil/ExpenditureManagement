"""
URL configuration for Exp_Management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import Expenses_App
from Expenses_App import views


urlpatterns = [
      path('admin', admin.site.urls),
    path('', Expenses_App.views.home, name='home'),
   path('login', Expenses_App.views.login_page, name='login'),
    path('register', Expenses_App.views.register_page, name='register'),
    path('logout',views.logout_page,name='logout'),


    path('expense', views.expense_manager, name='expense_manager'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('delete_income/<int:income_id>/', views.delete_income, name='delete_income'),
    path('delete_saving/<int:saving_id>/', views.delete_saving, name='delete_saving'),
    path('delete_budget/<int:budget_id>/', views.delete_budget, name='delete_budget'),

]
