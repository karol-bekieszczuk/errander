from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from .models import Errand
from .forms import DetailEditForm, CreateErrandForm
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import FormMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from simple_history.utils import update_change_reason
from itertools import chain
import csv


class CreateErrandView(LoginRequiredMixin, CreateView):
    template_name = 'errands/new.html'
    form_class = CreateErrandForm

    @method_decorator(permission_required('errands.create', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CreateErrandView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context


class UserErrandsList(LoginRequiredMixin, ListView):
    template_name = 'errands/index.html'
    context_object_name = 'errands'

    def get_queryset(self):
        if self.request.user.has_perm('errands.can_list_and_view_every_errand'):
            return Errand.objects.all()

        return Errand.objects.filter(assigned_users__in=[self.request.user.id])


class DetailErrandView(FormMixin, LoginRequiredMixin, DetailView):
    model = Errand
    template_name = 'errands/detail.html'
    form_class = DetailEditForm

    def get_initial(self):
        return {
            'assigned_users': self.get_object().assigned_users.all(),
            'status': self.get_object().status,
        }

    def get_form_kwargs(self):
        kwargs = super(DetailErrandView, self).get_form_kwargs()
        kwargs.update({
            'for_user': self.request.user,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        if self.request.user.has_perm('errands.access_history'):
            context['field_names'] = context['errand'].history.first()._meta.get_fields()
        return context

    def get_queryset(self):
        if self.request.user.has_perm('errands.can_list_and_view_every_errand'):
            return Errand.objects.filter(id=self.kwargs['pk'])

        return Errand.objects.filter(assigned_users__in=[self.request.user.id])


@login_required
@permission_required(perm='errands.create', raise_exception=True)
def create(request):
    if request.method == 'POST':
        form = CreateErrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, message='Errand created')
            return HttpResponseRedirect(reverse('errands:detail', args=[form.instance.id]))
    else:
        return redirect('errands:create')


@login_required
def update(request, pk: int):
    if request.method == 'POST':
        errand = get_object_or_404(Errand, pk=pk)
        form = DetailEditForm(request.POST)
        if form.is_valid():
            if request.user.has_perm('errands.assign_users'):
                errand.assigned_users.set(form.cleaned_data['assigned_users'])
            errand.status = request.POST['status']
            errand.save()
            update_change_reason(errand, request.POST['change_reason'])
            messages.success(request, message='Errand updated')
            return HttpResponseRedirect(reverse('errands:detail', args=[errand.id]))
    else:
        return render(request, reverse('errands:detail'), {'pk': pk})


@login_required
@permission_required(perm='errands.access_history', raise_exception=True)
def csv_history(request, pk: int) -> HttpResponse:
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="errand_history.csv"'},
    )

    errand_history = Errand.objects.get(pk=pk).history
    queryset_valueslist = errand_history.all().values_list(named=True)

    fields = list(errand_history.first()._meta.get_fields())
    fields.pop(0)
    field_names = (str(f.name) for f in fields)

    writer = csv.writer(response)
    writer.writerows(chain([field_names], queryset_valueslist))

    return response
