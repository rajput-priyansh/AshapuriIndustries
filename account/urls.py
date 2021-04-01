from django.conf.urls import url

from . import views
from .views import *

urlpatterns = [
    url(r'^$', GeneratePdf.as_view(), name='generate_pdf'),
    url('setting-gst/', SettingGSTList.as_view(), name='setting_GST_list'),
    url('active-customers/', ActiveCustomerList.as_view(), name='active_customer_list'),
    url('active-customers-mobile/', ActiveCustomerMobileList.as_view(), name='active_customer_list_mobile'),
    url(r'^signin/', LoginView.as_view(), name='signin'),
]