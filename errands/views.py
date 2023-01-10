# from django.http import HttpResponse
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
from .models import Errand
from .forms import DetailEditForm, DetailEditFormView
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages


class UserErrandsList(generic.ListView):
    template_name = 'errands/user_errands.html'
    context_object_name = 'user_errands'

    def get_queryset(self):
        return Errand.objects.filter(assigned_users__in=[self.request.user.id])


class ErrandDetailView(generic.DetailView):
    model = Errand
    template_name = 'errands/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DetailEditForm()
        context['status_string'] = Errand.STATUSES[context['errand'].status][1]
        context['last_change_reason'] = context['errand'].history.first().history_change_reason
        return context

    def get_queryset(self):
        return Errand.objects.filter(assigned_users__in=[self.request.user.id])


class DetailView(generic.DetailView):

    def get(self, request, *args, **kwargs):
        view = ErrandDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ErrandDetailView.as_view()
        return view(request, *args, **kwargs)


def update(request, errand_id):
    if request.method == 'POST':
        errand = get_object_or_404(Errand, pk=errand_id)
        form = DetailEditForm(request.POST)
        if form.is_valid():
            errand.status = request.POST['status']
            errand._change_reason = request.POST['change_reason']
            errand.save()
            messages.success(request, message='Errand updated')
            return HttpResponseRedirect(reverse('errands:detail', args=[errand.id]))
    else:
        return render(request, reverse('errands:detail'), {'errand_id': errand_id})
