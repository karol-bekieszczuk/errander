from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SignupForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from emails.tokens import TokenGenerator
from django.core.mail import EmailMessage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import User


class UserIndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'accounts/index.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.all()

    @method_decorator(permission_required('accounts.view_index', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UserIndexView, self).dispatch(*args, **kwargs)


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=self.request.user.id)
        if self.request.user.has_perm('accounts.view_any_user'):
            user = get_object_or_404(User, pk=self.kwargs['pk'])
        context['object'] = user
        context['user'] = self.request.user
        context['user_errands'] = user.errand_set.all()
        return context


@login_required
@permission_required('accounts.register_user')
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('emails/templates/acc_active_email.html', {
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
            messages.success(request, 'Invite sent')
            return HttpResponseRedirect(reverse('accounts:signup'))
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


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
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('accounts:login_user')
    else:
        messages.success(request, 'Activation link is invalid!')
        return redirect('accounts:login_user')


def login_user(request):
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'log in success')
            return redirect('accounts:profile', pk=user.id)
        else:
            messages.error(request, 'logging in error')
            return render(request, 'accounts/login.html', {})
    else:
        return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'log out success')
    return render(request, 'accounts/logged_out.html', {})
