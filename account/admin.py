from django.contrib import admin
from .models import *

# Register your models here.


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Account'
    fk_name = 'user'


class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'email',
        'mobile_number',
        'creation_date',
    ]
    list_filter = [
        'is_active',
        'is_approved',
        'is_favourite',
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
    ]

    fields = ['full_name', 'email', 'mobile_number', 'image', 'address', 'pan_number', 'gst_number',
              'is_approved', 'is_active', 'is_favourite', ]


class SettingAccountAdmin(admin.ModelAdmin):
    list_display = ['gst_number', 'discount', ]


class SettingGSTAdmin(admin.ModelAdmin):
    list_display = ['setting_cgst', 'setting_sgst', 'setting_igst', ]


class TermsConditionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'term_condition', ]


admin.site.register(Account, AccountAdmin)
admin.site.register(SettingAccount, SettingAccountAdmin)
admin.site.register(SettingGST, SettingGSTAdmin)
admin.site.register(TermsConditions, TermsConditionsAdmin)
