from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<order_id>[0-9]+)/(?P<invoice_type>[0-9]+)$', views.invoice, name='invoice'),
    url(r'^products/', views.ProductList.as_view(), name='products'),
    url(r'^products-mobile/', views.MobileProductList.as_view(), name='mobile_products'),
    url(r'^units/', views.UnitList.as_view(), name='units'),
    url(r'^units-mobile/', views.MobileUnitList.as_view(), name='mobile_units'),
    url(r'^customer-orders/', views.CustomerOrderList.as_view(), name='customer_order_list'),
    url(r'^customer-mobile-orders/', views.CustomerMobileOrderList.as_view(), name='customer_mobile_order_list'),
    url(r'^customer-order/', views.customer_order, name='customer_order'),
]
