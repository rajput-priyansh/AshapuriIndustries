from .models import *
from account.serializers import *
from account.models import *

from rest_framework import serializers
from django.contrib.auth.models import User
from num2words import num2words
import math


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'description']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_type', 'hsn_number']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'description']


class OrderProductsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    product_size = ProductSizeSerializer()
    unit = UnitSerializer()
    amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderProducts
        fields = ['id', 'weight', 'rate', 'product', 'product_size', 'unit', 'amount']

    def get_amount(self, p):
        return p.weight * p.rate


class OrderTotal:
    def __init__(self, total, cgst, sgst, igst, net_total, grand_total, discount, str_total_in_words, total_tax, order_total_rounded):
        self.total = total
        self.cgst = cgst
        self.sgst = sgst
        self.igst = igst
        self.net_total = net_total
        self.grand_total = grand_total
        self.discount = discount
        self.str_total_in_words = str_total_in_words
        self.total_tax = total_tax
        self.order_total_rounded = order_total_rounded


class OrderTotalSerializer(serializers.Serializer):
    total = serializers.CharField()
    cgst = serializers.CharField()
    sgst = serializers.CharField()
    igst = serializers.CharField()
    net_total = serializers.CharField()
    grand_total = serializers.CharField()
    discount = serializers.CharField()
    str_total_in_words = serializers.CharField()
    total_tax = serializers.CharField()
    order_total_rounded = serializers.CharField()


class CustomerOrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    host = serializers.SerializerMethodField(read_only=True)
    setting_account = serializers.SerializerMethodField(read_only=True)
    terms_conditions = serializers.SerializerMethodField(read_only=True)
    str_status = serializers.SerializerMethodField(read_only=True)
    str_creation_date = serializers.SerializerMethodField(read_only=True)
    str_delivery_date = serializers.SerializerMethodField(read_only=True)
    str_invoice_date = serializers.SerializerMethodField(read_only=True)
    order_total = serializers.SerializerMethodField(read_only=True)
    user = ProfileSerializer()

    class Meta:
        model = CustomerOrder
        fields = ['id', 'order_number', 'delivery_date', 'status', 'description', 'shipping_address', 'products',
                  'creation_date', 'user', 'host', 'setting_account', 'transportation_mode',
                  'vehicle_number', 'str_status', 'state_code', 'state', 'terms_conditions', 'str_creation_date',
                  'str_delivery_date', 'consignee_name', 'consignee_address', 'invoice_type', 'consignee_pan',
                  'consignee_gst', 'order_total', 'str_invoice_date']

    def get_products(self, obj):
        order_products = OrderProducts.objects.filter(customer_order=obj)
        if not order_products:
            return None
        return OrderProductsSerializer(order_products, many=True).data

    def get_host(self, obj):
        user = User.objects.first()
        if not user:
            return None
        return UserSerializer(user, many=False).data

    def get_setting_account(self, obj):
        sa = SettingAccount.objects.first()
        if not sa:
            return None
        return SettingAccountSerializer(sa, many=False).data

    def get_terms_conditions(self, obj):
        sa = TermsConditions.objects.all()
        if not sa:
            return None
        return TermsConditionsSerializer(sa, many=True).data

    def get_str_creation_date(self, obj):
        return obj.creation_date.strftime("%d-%m-%Y")

    def get_str_delivery_date(self, obj):
        return obj.delivery_date.strftime("%d-%m-%Y")

    def get_str_invoice_date(self, obj):
        return obj.invoice_date.strftime("%d-%m-%Y")

    def get_str_status(self, obj):
        switcher = {
            1: CustomerOrder.ORDER_PLACED,
            2: CustomerOrder.ORDER_READY,
            3: CustomerOrder.ORDER_DELIVERED,
        }
        return switcher.get(obj.status, "ND")

    def get_order_total(self, obj):
        order_products = OrderProducts.objects.filter(customer_order=obj)
        total = 0
        setting_account = obj.settingGST
        for product in order_products:
            total += product.weight * product.rate

        discount = 0
        cgst = 0
        sgst = 0
        igst = 0
        if setting_account:
            if setting_account.setting_cgst and setting_account.setting_cgst > 0:
                cgst = (setting_account.setting_cgst * total) / 100

            if setting_account.setting_sgst and setting_account.setting_sgst > 0:
                sgst = (setting_account.setting_sgst * total) / 100

            if setting_account.setting_igst and setting_account.setting_igst > 0:
                igst = (setting_account.setting_igst * total) / 100

        net_amt = total + cgst + sgst + igst

        if setting_account and setting_account.discount and setting_account.discount > 0:
            discount = (setting_account.discount * net_amt) / 100

        grand_total = round(net_amt - (discount + obj.discount))
        str_total_in_words = (num2words(grand_total, to='cardinal', lang='en_IN').upper()).replace("AND", "").replace(
            ",", "").replace("-", "")

        total_tax = cgst + sgst + igst
        str_order_total_rounded = "0.0"

        order_total_rounded, whole = math.modf(net_amt)
        if order_total_rounded < 0.5:
            str_order_total_rounded = "-0." + str(str(net_amt).split(".")[1])
        else:
            str_order_total_rounded = "+0." + str(str(net_amt).split(".")[1])

        order_tot = OrderTotal(cgst=cgst, sgst=sgst, igst=igst, discount=discount, net_total=net_amt,
                               grand_total=grand_total, total=total, str_total_in_words=str_total_in_words,
                               total_tax=total_tax, order_total_rounded=str_order_total_rounded)
        return OrderTotalSerializer(order_tot, many=False).data
