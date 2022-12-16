from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from hashlib import sha1


def login_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, 'log in success')
        return redirect('/accounts/profile')
    else:
        messages.success(request, 'logging in error')
        return render(request, 'accounts/login.html', {})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
