"""Top level HTTP request routing."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/dash/'), name='home-redirect'),
    path('dash/', admin.site.urls, name='admin'),
    path('key/', include('stethoscope.apps.licensing.urls', namespace='licensing')),
]
