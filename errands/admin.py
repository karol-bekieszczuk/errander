from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Errand
from .forms import CreateErrandForm


class ErrandAdmin(SimpleHistoryAdmin):
    form = CreateErrandForm

    def save_model(self, request, obj, form, change):
        obj._change_reason = form.cleaned_data["change_reason"]
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        obj._change_reason = "deletion"
        obj.delete()

    def delete_queryset(self, request, queryset):
        for errand in queryset:
            errand._change_reason = "deletion"
            errand.delete()


admin.site.register(Errand, ErrandAdmin)
