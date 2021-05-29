from .models import *
from account.serializers import *
from account.models import *

from rest_framework import serializers
from django.contrib.auth.models import User
from num2words import num2words
import math


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'hsn_number']


class BagWightUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BagWightUnit
        fields = ['id', 'display_name', 'wight', 'unit', 'description']


class OrderProductGst:
    def __init__(self, cgst, sgst, igst):
        self.cgst = cgst
        self.sgst = sgst
        self.igst = igst


class OrderProductGstSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    cgst = serializers.CharField()
    sgst = serializers.CharField()
    igst = serializers.CharField()


class OrderProductsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    bag_wight_unit = BagWightUnitSerializer()
    amount = serializers.SerializerMethodField(read_only=True)
    weight = serializers.SerializerMethodField(read_only=True)
    order_product_gst = serializers.SerializerMethodField(read_only=True)
    settingGST = SettingGSTSerializer()

    class Meta:
        model = OrderProducts
        fields = ['id', 'weight', 'rate', 'product', 'no_of_bag', 'bag_wight_unit', 'amount', 'settingGST', 'order_product_gst']

    def get_amount(self, p):
        return (p.no_of_bag * p.bag_wight_unit.wight) * p.rate

    def get_weight(self, p):
        return p.no_of_bag * p.bag_wight_unit.wight

    def get_order_product_gst(self, p):
        cgst = 0
        sgst = 0
        igst = 0

        a_total = (p.bag_wight_unit.wight * p.no_of_bag) * p.rate

        if p.settingGST:
            if p.settingGST.setting_cgst and p.settingGST.setting_cgst > 0:
                cgst = (p.settingGST.setting_cgst * a_total) / 100

            if p.settingGST.setting_sgst and p.settingGST.setting_sgst > 0:
                sgst = (p.settingGST.setting_sgst * a_total) / 100

            if p.settingGST.setting_igst and p.settingGST.setting_igst > 0:
                igst = (p.settingGST.setting_igst * a_total) / 100

        order_product = OrderProductGst(cgst=cgst, sgst=sgst, igst=igst)
        return OrderProductGstSerializer(order_product, many=False).data


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
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

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
    str_invoice_date = serializers.SerializerMethodField(read_only=True)
    order_total = serializers.SerializerMethodField(read_only=True)
    user = ProfileSerializer()

    class Meta:
        model = CustomerOrder
        fields = ['id', 'invoice_number', 'challan_number', 'status', 'products',
                  'creation_date', 'user', 'host', 'setting_account', 'transportation_mode',
                  'vehicle_number', 'str_status', 'state_code', 'state', 'terms_conditions', 'str_creation_date',
                  'invoice_type', 'order_total', 'str_invoice_date', 'packaging_total']

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
        setting_account = SettingAccount.objects.last()

        discount = 0
        cgst = 0
        sgst = 0
        igst = 0

        for product in order_products:
            total += (product.bag_wight_unit.wight * product.no_of_bag) * product.rate
            a_total = (product.bag_wight_unit.wight * product.no_of_bag) * product.rate

            if product.settingGST:
                if product.settingGST.setting_cgst and product.settingGST.setting_cgst > 0:
                    cgst += (product.settingGST.setting_cgst * a_total) / 100

                if product.settingGST.setting_sgst and product.settingGST.setting_sgst > 0:
                    sgst += (product.settingGST.setting_sgst * a_total) / 100

                if product.settingGST.setting_igst and product.settingGST.setting_igst > 0:
                    igst += (product.settingGST.setting_igst * a_total) / 100

        net_amt = round((total + cgst + sgst + igst + obj.packaging_total), 2)

        if setting_account and setting_account.discount and setting_account.discount > 0:
            discount = (setting_account.discount * net_amt) / 100

        order_total_rounded, whole = math.modf(net_amt)

        grand_total = round((net_amt - (discount + obj.discount)), 2) - order_total_rounded
        str_total_in_words = (num2words(grand_total, to='cardinal', lang='en_IN').upper()).replace("AND", "").replace(
            ",", "").replace("-", "")

        total_tax = round((cgst + sgst + igst), 2)
        str_order_total_rounded = "0.0"

        if order_total_rounded < 0.5:
            str_order_total_rounded = "-0." + str(str(net_amt).split(".")[1])
        else:
            str_order_total_rounded = "+0." + str(str(net_amt).split(".")[1])

        order_tot = OrderTotal(cgst=cgst, sgst=sgst, igst=igst, discount=discount, net_total=net_amt,
                               grand_total=grand_total, total=total, str_total_in_words=str_total_in_words,
                               total_tax=total_tax, order_total_rounded=str_order_total_rounded)
        return OrderTotalSerializer(order_tot, many=False).data
