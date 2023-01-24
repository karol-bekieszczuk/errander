from django import forms
from .models import Errand
from accounts.models import User
from permissionedforms import PermissionedForm
from django.core.exceptions import ValidationError


class CreateErrandForm(forms.ModelForm):
    class Meta:
        model = Errand
        exclude = ['status']
        widgets = {
            'assigned_users': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(CreateErrandForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs['id'] = 'autocomplete'
        self.fields['address'].widget.attrs['name'] = 'autocomplete'


class DetailEditForm(PermissionedForm):
    status = forms.IntegerField(label="Errand status", widget=forms.Select(choices=Errand.STATUSES))
    change_reason = forms.CharField(label="Note", max_length=100)
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign users'
    )

    class Meta:
        model = Errand
        field_permissions = {
            'assigned_users': 'errands.assign_users'
        }

