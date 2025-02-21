from django.urls import path
from Expenses_App import views

 #URLConf
urlpatterns=[
        path("",views.home,name="home"),
        path("login/", views.login_page, name="login"),
        path("register/", views.register_page, name="register"),
        path('table/',views.table,name="table"),
        path('logout/',views.logout_page,name='logout')

    ]