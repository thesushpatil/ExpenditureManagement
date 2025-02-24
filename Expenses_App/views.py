from django.shortcuts import render, redirect
from django.db import models
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
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
                return redirect('expense')



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

# @login_required(login_url='/login/')
# def table(request):
#     return render(request,'table.html')


def logout_page(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def expense(request):
    return render(request,'expense.html')