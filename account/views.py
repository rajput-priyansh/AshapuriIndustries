# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.http import HttpResponse
from django.views.generic import View
from .utils import render_to_pdf
from rest_framework import generics
from .serializers import *
from rest_framework.permissions import AllowAny
from rest_framework import (
    status,
    views,
    viewsets,
)
from AshapuriIndustries.utils import generate_jwt_token
from rest_framework.response import Response


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        data = {
            'today': datetime.date.today(),
            'amount': 39000.99,
            'customer_name': 'Priyansh Rajput',
            'order_id': 1233434,
        }
        pdf = render_to_pdf('accounts/invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class ActiveCustomerList(generics.ListCreateAPIView):
    queryset = Account.objects.filter(is_approved=True).order_by('-is_favourite')
    serializer_class = ProfileSerializer


class ActiveCustomerMobileList(generics.ListCreateAPIView):
    queryset = Account.objects.filter(is_approved=True).order_by('-is_favourite')
    serializer_class = ProfileSerializer

    def list(self, request):
        try:
            queryset = self.get_queryset()
            serializer = ProfileSerializer(queryset, many=True)
            return Response({"status": 1, "data": serializer.data})
        except:
            return Response({"status": 0})


class LoginView(views.APIView):
    serializer_class = LoginSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request, format=None):
        data = request.data.copy()
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            user = serializer.get_user(data['username'])
            simpleJWT = generate_jwt_token(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': simpleJWT['access'],
                'refresh': simpleJWT['refresh']
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SettingGSTList(generics.ListCreateAPIView):
    queryset = SettingGST.objects.all()
    serializer_class = SettingGSTSerializer
