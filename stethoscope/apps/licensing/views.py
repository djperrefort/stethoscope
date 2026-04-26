"""Endpoint handlers used to define request/response logic."""

from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Deployment, HeartBeat, LicenseToken
from .serializers import (
    ActivateRequestSerializer,
    DeactivateRequestSerializer,
    HeartBeatRequestSerializer,
    ValidateRequestSerializer,
)
from .shortcuts import hash_token, resolve_client_ip

__all__ = [
    'ActivateView',
    'DeactivateView',
    'HeartBeatView',
    'RetrieveView',
    'ValidateView',
]


class ActivateView(APIView):
    """Endpoint for registering a deployment against a license token."""

    @staticmethod
    def post(request: Request) -> Response:
        """Register a deployment identifier and return the activation status.

        If the identifier is already registered to the token the request is
        treated as idempotent and returns 200 without consuming an additional
        seat. New identifiers are rejected with a 4xx when the token has
        reached its deployment limit.
        """

        serializer = ActivateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hashed_token = hash_token(serializer.validated_data['token'])
        identifier = serializer.validated_data['identifier']

        try:
            token = LicenseToken.objects.get(token=hashed_token, enabled=True)

        except LicenseToken.DoesNotExist:
            return Response(
                {'non_field_errors': ['No active license token found for the given value.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Idempotent: already-registered identifiers always succeed
        if Deployment.objects.filter(license_token=token, identifier=identifier).exists():
            return Response(status=status.HTTP_200_OK)

        # Enforce deployment limit when one is set
        if token.max_deployments is not None:
            current_count = Deployment.objects.filter(license_token=token).count()
            if current_count >= token.max_deployments:
                return Response(
                    {'non_field_errors': ['Deployment limit reached for this license token.']},
                    status=status.HTTP_403_FORBIDDEN,
                )

        try:
            Deployment.objects.create(license_token=token, identifier=identifier)

        except IntegrityError:
            # A concurrent request registered the same identifier between the
            # exists() check and the create() call — treat as idempotent.
            pass

        return Response(status=status.HTTP_200_OK)


class DeactivateView(APIView):
    """Endpoint for removing a registered deployment from a license token."""

    @staticmethod
    def post(request: Request) -> Response:
        """Remove a deployment identifier and free the associated seat.

        Returns 200 whether or not the identifier was registered. Returns a
        4xx when the token does not permit deactivation.
        """

        serializer = DeactivateRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hashed_token = hash_token(serializer.validated_data['token'])
        identifier = serializer.validated_data['identifier']

        try:
            token = LicenseToken.objects.get(token=hashed_token, enabled=True)

        except LicenseToken.DoesNotExist:
            return Response(
                {'non_field_errors': ['No active license token found for the given value.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not token.allow_deactivation:
            return Response(
                {'non_field_errors': ['Deactivation is not permitted for this license token.']},
                status=status.HTTP_403_FORBIDDEN,
            )

        Deployment.objects.filter(license_token=token, identifier=identifier).delete()
        return Response(status=status.HTTP_200_OK)


class HeartBeatView(APIView):
    """Endpoint for recording application deployments running under a license token."""

    @staticmethod
    def post(request: Request) -> Response:
        """Record a deployment heartbeat and return an empty 200 response.

        Applications are allowed to check in using expired or inactive tokens.
        This allows administrators to track customers who may need assistance
        requesting or migrating to a new token.
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


class RetrieveView(APIView):
    """Browser-facing endpoint for one-time retrieval of a plaintext license token."""

    @staticmethod
    def get(request: Request, retrieve_id: str):
        """Render a page warning the user that retrieval is a one-time action.

        Args:
            request: An incoming HTTP request.
            retrieve_id: The retrieval ID from the URL.

        Returns:
            A rendered HTML response.
        """

        try:
            token = LicenseToken.objects.select_related('customer', 'application').get(
                retrieve_id=retrieve_id,
                enabled=True,
            )

        except LicenseToken.DoesNotExist:
            return render(request, 'licensing/retrieve_not_found.html', status=404)

        if token.is_retrieved:
            return render(request, 'licensing/retrieve_already_retrieved.html', status=410)

        return render(request, 'licensing/retrieve_confirm.html', {
            'token': token,
            'retrieve_id': retrieve_id,
        })

    @staticmethod
    def post(request: Request, retrieve_id: str):
        """Render a page revealing the plaintext token.

        The token is automatically marked as retrieved, preventing it from
        being accessed a second time.

        Args:
            request: An incoming HTTP request.
            retrieve_id: The retrieval ID from the URL.

        Returns:
            A rendered HTML response.
        """

        try:
            token = LicenseToken.objects.select_related('customer', 'application').get(
                retrieve_id=retrieve_id,
                enabled=True,
            )

        except LicenseToken.DoesNotExist:
            return render(request, 'licensing/retrieve_not_found.html', status=404)

        if token.is_retrieved:
            return render(request, 'licensing/retrieve_already_retrieved.html', status=410)

        token_plain = token.token_plain
        token.mark_retrieved()

        return render(request, 'licensing/retrieve_token.html', {
            'token': token,
            'token_plain': token_plain,
        })


class ValidateView(APIView):
    """Endpoint for confirming whether a license token is currently active."""

    @staticmethod
    def post(request: Request) -> Response:
        """Return a JSON response containing the expiration time for a provided token.

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
                enabled=True,
            )

        except LicenseToken.DoesNotExist:
            return Response(
                {'non_field_errors': ['No active license token found for the given value.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'expires_at': token.expires_at})
