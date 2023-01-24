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
from django.conf import settings
from simple_history.utils import update_change_reason


class CreateErrandView(LoginRequiredMixin, generic.CreateView):
    template_name = 'errands/new.html'
    form_class = CreateErrandForm

    @method_decorator(permission_required('errands.create', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CreateErrandView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context

class UserErrandsList(LoginRequiredMixin, generic.ListView):
    template_name = 'errands/index.html'
    context_object_name = 'errands'

    def get_queryset(self):
        if self.request.user.has_perm('errands.can_list_and_view_every_errand'):
            return Errand.objects.all()

        return Errand.objects.filter(assigned_users__in=[self.request.user.id])


class ErrandDetailView(LoginRequiredMixin, generic.DetailView):
    model = Errand
    template_name = 'errands/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DetailEditForm(
            for_user=self.request.user,
            initial={
                'assigned_users': context['errand'].assigned_users.all(),
            }
        )
        context['status_string'] = Errand.STATUSES[context['errand'].status][1]
        context['last_change_reason'] = context['errand'].history.first().history_change_reason
        context['google_api_key'] = settings.GOOGLE_API_KEY

        return context

    def get_queryset(self):
        if self.request.user.has_perm('errands.can_list_and_view_every_errand'):
            return Errand.objects.filter(id=self.kwargs['pk'])

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
            messages.success(request, message='Errand created')
            return HttpResponseRedirect(reverse('errands:detail', args=[form.instance.id]))
    else:
        return redirect('errands:create')


@login_required
def update(request, errand_id):
    if request.method == 'POST':
        errand = get_object_or_404(Errand, pk=errand_id)
        form = DetailEditForm(request.POST)
        if form.is_valid():
            if request.user.has_perm('errands.assign_users') and form.cleaned_data['assigned_users']:
                errand.assigned_users.set(form.cleaned_data['assigned_users'])
            errand.status = request.POST['status']
            errand.save()
            update_change_reason(errand, request.POST['change_reason'])
            messages.success(request, message='Errand updated')
            return HttpResponseRedirect(reverse('errands:detail', args=[errand.id]))
    else:
        return render(request, reverse('errands:detail'), {'errand_id': errand_id})
