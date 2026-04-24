"""Top level HTTP request routing."""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path('', lambda *args: HttpResponse(), name='home'),
    path('dash/', admin.site.urls, name='admin'),
    path('key/', include('stethoscope.apps.licensing.urls', namespace='licensing')),
]
