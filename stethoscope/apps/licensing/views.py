"""Endpoint handlers used to define request/response processing logic."""

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HeartBeat, LicenseToken
from .serializers import HeartBeatRequestSerializer, ValidateRequestSerializer
from .shortcuts import hash_token, resolve_client_ip

__all__ = [
    'HeartBeatView',
    'ValidateView',
]


class ValidateView(APIView):
    """Endpoint for confirming whether a license token is currently active."""

    @staticmethod
    def post(request: Request) -> Response:
        """Return the expiration time for a provided token.

         Valid, currently active tokens are returned a 200 response containing
         the token's expiration time. Invalid or inactive tokens are returned
         a 400 error.
         """

        # Validate the request payload
        serializer = ValidateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Hash token for use in DB queries
        now = timezone.now()
        hashed_token = hash_token(serializer.validated_data['token'])

        # Check the database for a valid, active token
        try:
            token = LicenseToken.objects.get(
                Q(expires_at__gte=now) | Q(expires_at__isnull=True),
                token=hashed_token,
                starts_at__lte=now,
            )

        except LicenseToken.DoesNotExist:
            return Response(
                {'non_field_errors': ['No active license token found for the given value.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'expires_at': token.expires_at})


class HeartBeatView(APIView):
    """Endpoint for recording application deployments running under a license token."""

    @staticmethod
    def post(request: Request) -> Response:
        """Record a deployment heartbeat and return an empty 200 response.

        Applications are allowed to check in using expired or inactive tokens.
        This allows administrators to track customers who may need assistance
        requesting/migrating to a new token.
        """

        # Validate the request payload
        serializer = HeartBeatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Hash token for use in DB queries
        hashed_token = hash_token(serializer.validated_data['token'])

        # Check the database for a valid token
        try:
            token = LicenseToken.objects.get(token=hashed_token)

        except LicenseToken.DoesNotExist:
            return Response(
                {'non_field_errors': ['No license token found for the given value.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log the heartbeat request
        HeartBeat.objects.create(
            license_token=token,
            uuid=serializer.validated_data['uuid'],
            ip=resolve_client_ip(request),
        )

        return Response(status=status.HTTP_200_OK)
