from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from .models import Errand
from .forms import DetailEditForm, CreateErrandForm
from django.views import generic
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class CreateErrandView(LoginRequiredMixin, generic.CreateView):
    template_name = 'errands/new.html'
    form_class = CreateErrandForm

    @method_decorator(permission_required('errands.create', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CreateErrandView, self).dispatch(*args, **kwargs)


class UserErrandsList(LoginRequiredMixin, generic.ListView):
    template_name = 'errands/user_errands.html'
    context_object_name = 'user_errands'

    def get_queryset(self):
        return Errand.objects.filter(assigned_users__in=[self.request.user.id])


class ErrandDetailView(LoginRequiredMixin, generic.DetailView):
    model = Errand
    template_name = 'errands/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DetailEditForm(for_user=self.request.user)
        context['status_string'] = Errand.STATUSES[context['errand'].status][1]
        context['last_change_reason'] = context['errand'].history.first().history_change_reason
        return context

    def get_queryset(self):
        return Errand.objects.filter(assigned_users__in=[self.request.user.id])


class DetailView(LoginRequiredMixin, generic.DetailView):
    def get(self, request, *args, **kwargs):
        view = ErrandDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ErrandDetailView.as_view()
        return view(request, *args, **kwargs)


@permission_required(perm='errands.create', raise_exception=True)
def create(request):
    if request.method == 'POST':
        form = CreateErrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.error(request, message='Errand created')
            return HttpResponseRedirect(reverse('errands:detail', args=[form.instance.id]))
    else:
        return redirect('errands:create')


@login_required
def update(request, errand_id):
    if request.method == 'POST':
        errand = get_object_or_404(Errand, pk=errand_id)
        form = DetailEditForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['assigned_users'] and request.user.has_perm('errands.assign_users'):
                for u in form.cleaned_data['assigned_users']:
                    errand.assigned_users.add(u)
            errand.status = request.POST['status']
            errand._change_reason = request.POST['change_reason']
            errand.save()
            messages.success(request, message='Errand updated')
            return HttpResponseRedirect(reverse('errands:detail', args=[errand.id]))
    else:
        return render(request, reverse('errands:detail'), {'errand_id': errand_id})


# @permission_required('errands.assign_users')
# def add_users_to_errand(request, errand_id):
#     if request.method == 'POST':
#         errand = get_object_or_404(Errand, pk=errand_id)
#         form = AddUsersToErrandForm(request.POST)
#         if form.is_valid():
#             errand._change_reason = "added user to errand"
#             errand.save()
#             messages.success(request, message='Errand updated')
#             return HttpResponseRedirect(reverse('errands:add_users_to_errand', args=[errand_id]))
#     else:
#         return render(request, reverse('errands:detail'), {'errand_id': errand_id})