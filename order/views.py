# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .utils import render_to_pdf
from rest_framework import generics, permissions
from .serializers import *
from django.shortcuts import get_object_or_404
from account.models import SettingAccount, Account
from django.contrib.auth.models import User


def invoice(request, order_id, invoice_type):
    order = get_object_or_404(CustomerOrder, pk=order_id)
    order.invoice_type = invoice_type
    order.save()
    serializer = CustomerOrderSerializer(order)
    # print('serializer data:', serializer.data)
    pdf = render_to_pdf('order/invoice.html', serializer.data)
    return HttpResponse(pdf, content_type='application/pdf')


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class MobileProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request):
        try:
            queryset = self.get_queryset()
            serializer = ProductSerializer(queryset, many=True)
            return Response({"status": 1, "data": serializer.data})
        except:
            return Response({"status": 0})


class UnitList(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class MobileUnitList(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

    def list(self, request):
        try:
            queryset = self.get_queryset()
            serializer = UnitSerializer(queryset, many=True)
            return Response({"status": 1, "data": serializer.data})
        except:
            return Response({"status": 0})


class ProductSizeList(generics.ListCreateAPIView):
    queryset = ProductSize.objects.all()
    serializer_class = ProductSizeSerializer


class MobileProductSizeList(generics.ListCreateAPIView):
    queryset = ProductSize.objects.all()
    serializer_class = ProductSizeSerializer

    def list(self, request):
        try:
            queryset = self.get_queryset()
            serializer = ProductSizeSerializer(queryset, many=True)
            return Response({"status": 1, "data": serializer.data})
        except:
            return Response({"status": 0})


@api_view(['POST'], )
@permission_classes([permissions.AllowAny])
def customer_order(request):
    if request.method == 'POST':
        order = request.data.get('order')
        products = request.data.get('products')

        # print(order)
        print(products)

        if order and products:
            try:
                customer_order = CustomerOrder()

                customer_order.user = Account.objects.get(pk=order['user'])
                customer_order.settingGST = SettingGST.objects.get(pk=order['settingGst'])

                if 'description' in order and order['description']:
                    customer_order.description = order['description']

                if 'shipping_address' in order and order['shipping_address']:
                    customer_order.shipping_address = order['shipping_address']

                if 'discount' in order and order['discount']:
                    customer_order.discount = order['discount']

                if 'delivery_date' in order and order['delivery_date']:
                    customer_order.delivery_date = order['delivery_date']

                if 'invoice_date' in order and order['invoice_date']:
                    customer_order.invoice_date = order['invoice_date']

                if 'transportation_mode' in order and order['transportation_mode']:
                    customer_order.transportation_mode = order['transportation_mode']

                if 'vehicle_number' in order and order['vehicle_number']:
                    customer_order.vehicle_number = order['vehicle_number']

                if 'state' in order and order['state']:
                    customer_order.state = order['state']

                if 'state_code' in order and order['state_code']:
                    customer_order.state_code = order['state_code']

                if 'consignee_name' in order and order['consignee_name']:
                    customer_order.consignee_name = order['consignee_name']

                if 'consignee_address' in order and order['consignee_address']:
                    customer_order.consignee_address = order['consignee_address']

                if 'consignee_pan' in order and order['consignee_pan']:
                    customer_order.consignee_pan = order['consignee_pan']

                if 'consignee_gst' in order and order['consignee_gst']:
                    customer_order.consignee_gst = order['consignee_gst']

                if 'order_number' in order and order['order_number']:
                    customer_order.order_number = order['order_number']

                customer_order.save()

                total = 0
                for product in products:
                    p = OrderProducts(product=Product.objects.get(pk=product['product']),
                                      product_size=ProductSize.objects.get(pk=product['size']),
                                      unit=Unit.objects.get(pk=product['unit']),
                                      weight=product['weight'],
                                      rate=product['rate'], customer_order=customer_order)
                    total += p.weight * p.rate
                    p.save()

                customer_order.total = total

                customer_order.save()

            except(User.DoesNotExist, Product.DoesNotExist, ProductSize.DoesNotExist, Unit.DoesNotExist):
                return Response({"status": 0, "result": "Data Does not exit"})

            return Response({"status": 1, "result": "Added data"})
        else:
            return Response({"status": 0, "result": "Invalid data"})
    else:
        return Response({"status": 0, "result": "Invalid method type"})


class CustomerOrderList(generics.ListCreateAPIView):
    queryset = CustomerOrder.objects.all().order_by('-creation_date')
    serializer_class = CustomerOrderSerializer


class CustomerMobileOrderList(generics.ListCreateAPIView):
    queryset = CustomerOrder.objects.all().order_by('-creation_date')
    serializer_class = CustomerOrderSerializer

    def list(self, request):
        try:
            queryset = self.get_queryset()
            serializer = CustomerOrderSerializer(queryset, many=True)
            return Response({"status": 1, "data": serializer.data})
        except:
            return Response({"status": 0})
