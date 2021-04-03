# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from AshapuriIndustries import settings
from .models import *


class BagWightUnitAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'wight', 'unit', 'description']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_type', 'hsn_number']


class ChoiceOrderProductInline(admin.TabularInline):
    model = OrderProducts
    extra = 1


class CustomerOrderAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    # filter_horizontal = ['order_products']
    list_display = ['customer_user', 'original_invoice', 'duplicate_invoice', 'triplicate_invoice', 'order_number',
                    'shipping_address', 'total', 'cgst', 'sgst', 'igst', 'grand_total', 'creation_date',
                    'delivery_date', 'all_order_product']
    list_filter = [
        'status',
    ]
    search_fields = [
        'user__email',
        'user__full_name',
    ]

    fields = ['user', 'delivery_date', 'invoice_date', 'status', 'invoice_type', 'description', 'shipping_address',
              'state', 'state_code', 'transportation_mode', 'vehicle_number', 'settingGST']

    inlines = [ChoiceOrderProductInline]

    def customer_user(self, obj):
        return "{}".format(obj.user.full_name)

    def original_invoice(self, obj):
        return '<a href="%s/%s/%s" target="_blank">%s</a>' % (
        settings.DOMAIN_NAME + '/order', obj.id, 1, 'Original Invoice')

    def duplicate_invoice(self, obj):
        return '<a href="%s/%s/%s" target="_blank">%s</a>' % (
        settings.DOMAIN_NAME + '/order', obj.id, 2, 'Duplicate Invoice')

    def triplicate_invoice(self, obj):
        return '<a href="%s/%s/%s" target="_blank">%s</a>' % (
        settings.DOMAIN_NAME + '/order', obj.id, 3, 'Triplicate Invoice')

    original_invoice.allow_tags = True
    original_invoice.short_description = 'Original Invoice'

    duplicate_invoice.allow_tags = True
    duplicate_invoice.short_description = 'Duplicate Invoice'

    triplicate_invoice.allow_tags = True
    triplicate_invoice.short_description = 'Triplicate Invoice'


admin.site.register(BagWightUnit, BagWightUnitAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CustomerOrder, CustomerOrderAdmin)
