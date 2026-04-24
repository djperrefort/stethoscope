"""Module level HTTP request routing."""

from django.urls import path

from .views import HeartBeatView, RetrieveView, ValidateView

app_name = 'licensing'

urlpatterns = [
    path('validate/', ValidateView.as_view(), name='validate'),
    path('heartbeat/', HeartBeatView.as_view(), name='heartbeat'),
    path('r/<str:retrieve_id>/', RetrieveView.as_view(), name='retrieve'),
]
