from django import forms
from .models import Errand
from accounts.models import User
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from permissionedforms import PermissionedForm


class CreateErrandForm(forms.ModelForm):

    class Meta:
        model = Errand
        exclude = ['status']
        widgets = {
            'assigned_users': forms.CheckboxSelectMultiple
        }

    change_reason = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super(CreateErrandForm, self).__init__(*args, **kwargs)
        self.fields['change_reason'].required = False


class DetailEditForm(PermissionedForm):
    status = forms.IntegerField(label="Errand status", widget=forms.Select(choices=Errand.STATUSES))
    change_reason = forms.CharField(label="Note", max_length=100)
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Errand
        field_permissions = {
            'assigned_users': 'errands.assign_users'
        }


# class DetailEditFormView(SingleObjectMixin, FormView):
#     template_name = 'errands/detail.html'
#     form_class = DetailEditForm
#     model = Errand
#     def __init__(self, **kwargs):
#         super().__init__(kwargs)
#         self.object = None
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return super().post(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse('errands:detail', kwargs={'errand_id': self.object.pk})
