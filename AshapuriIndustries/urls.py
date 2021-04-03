"""AshapuriIndustries URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

from AshapuriIndustries import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^accounts/', include('account.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^order/', include('order.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/add-new-order/$', TemplateView.as_view(template_name='admin/add_order.html'), name='add-new-order'),
    url(r'^admin/add-new-purchase/$', TemplateView.as_view(template_name='admin/add_purchase.html'), name='add-new-purchase'),
    url(r'^admin/customer-order-list/$', TemplateView.as_view(template_name='admin/customer_order_list.html'), name='customer-order-list'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Ashapuri Industries Admin"
admin.site.site_title = "Ashapuri Industries Admin Portal"
admin.site.index_title = "Welcome to Ashapuri Industries Portal"
