from django.contrib import admin

from .models import PensionCompany


@admin.register(PensionCompany)
class PensionCompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'registration_number',
        'data_created_at'
    ]
