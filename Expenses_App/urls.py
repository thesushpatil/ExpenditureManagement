from django.urls import path
from Expenses_App import views

 #URLConf
urlpatterns=[
        path("",views.home,name="home"),
        path("login/", views.login_page, name="login"),
        path("register/", views.register_page, name="register"),
        path('logout/',views.logout_page,name='logout'),


path('expense/', views.expense_manager, name='expense_manager'),
    path('delete_expense/<int:expense_id>', views.delete_expense, name='delete_expense'),
    path('delete_income/<int:income_id>', views.delete_income, name='delete_income'),
    path('delete_saving/<int:saving_id>', views.delete_saving, name='delete_saving'),
    path('delete_budget/<int:budget_id>', views.delete_budget, name='delete_budget'),

    ]