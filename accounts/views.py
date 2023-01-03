from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from emails.forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from emails.tokens import TokenGenerator
from django.core.mail import EmailMessage


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': TokenGenerator().make_uid(user),
                'token': TokenGenerator().make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, 'Please confirm your email address to complete the registration')
            return redirect('accounts:login_user')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    user_model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user_model.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None

    if user is not None and TokenGenerator().check_token(user, token):
        if user.token_expired():
            messages.success(request, 'Token expired, ask your manager for new link')
            return redirect('accounts:login_user')
            # TODO make custom errors
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('accounts:login_user')
    else:
        messages.success(request, 'Activation link is invalid!')
        return redirect('accounts:login_user')


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
