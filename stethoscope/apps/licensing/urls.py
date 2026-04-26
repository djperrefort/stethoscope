"""Module level HTTP request routing."""

from django.urls import path

from .views import ActivateView, DeactivateView, HeartBeatView, RetrieveView, ValidateView

app_name = 'licensing'

urlpatterns = [
    path('validate/', ValidateView.as_view(), name='validate'),
    path('heartbeat/', HeartBeatView.as_view(), name='heartbeat'),
    path('activate/', ActivateView.as_view(), name='activate'),
    path('deactivate/', DeactivateView.as_view(), name='deactivate'),
    path('r/<str:retrieve_id>/', RetrieveView.as_view(), name='retrieve'),
]
