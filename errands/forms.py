from django import forms
from .models import Errand
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin


class CustomAdminErrandForm(forms.ModelForm):
    class Meta:
        model = Errand
        fields = "__all__"

    change_reason = forms.CharField(max_length=100)


class DetailEditForm(forms.Form):
    status = forms.IntegerField(label="Errand status", widget=forms.Select(choices=Errand.STATUSES))
    change_reason = forms.CharField(label="Note", max_length=100)


class DetailEditFormView(SingleObjectMixin, FormView):
    template_name = 'errands/detail.html'
    form_class = DetailEditForm
    model = Errand

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.object = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('errands:detail', kwargs={'errand_id': self.object.pk})
