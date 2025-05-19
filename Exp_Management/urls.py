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
    path("", views.welcome, name="welcome"),
     # path('', views.home, name='home'),
     path("home",views.home_page,name="home"),

   path('login', Expenses_App.views.login_page, name='login'),
    path('register', Expenses_App.views.register_page, name='register'),
    path('logout',views.logout_page,name='logout'),
path('aboutus',views.about_us,name='aboutus'),

    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('delete_income/<int:income_id>/', views.delete_income, name='delete_income'),
    path('delete_saving/<int:saving_id>/', views.delete_saving, name='delete_saving'),
    path('delete_budget/<int:budget_id>/', views.delete_budget, name='delete_budget'),


    path('income', views.income, name='income'),
    path('expenses', views.expense_view, name='expenses'),
    path('budget', views.budget_view, name='budget'),
    path('savings', views.saving_view, name='savings'),

path('expenses/pdf', views.generate_expense_pdf, name='generate_expense_pdf'),

    path("chatbot", views.chatbot_view, name="chatbot"),

]
