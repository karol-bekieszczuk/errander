from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'log in success')
            return redirect('accounts:profile')
        else:
            messages.success(request, 'logging in error')
            return render(request, 'accounts/login.html', {})
    else:
        return render(request, 'accounts/login.html', {})

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'log out success')
        return render(request, 'accounts/logged_out.html', {})
    else:
        messages.success(request, 'you are not logged in')
        return redirect('accounts:login_user')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
