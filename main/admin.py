from django.contrib import admin

from .models import PensionCompany
from .utils import reload_pension_company


@admin.register(PensionCompany)
class PensionCompanyAdmin(admin.ModelAdmin):
    def reload(modeladmin, request, queryset):
        reload_pension_company()

    list_display = [
        'name',
        'registration_number',
        'data_created_at'
    ]
    
    actions = [
        'reload'
    ]

    reload.short_description="국민연금 데이터 다시 불러오기"
