"""Serializers for parsing and validating HTTP request content."""

from rest_framework import serializers

__all__ = [
    'ActivateRequestSerializer',
    'DeactivateRequestSerializer',
    'HeartBeatRequestSerializer',
    'ValidateRequestSerializer',
]


class ActivateRequestSerializer(serializers.Serializer):
    """Enforces content schemas for deployment activation requests."""

    identifier = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=64)


class DeactivateRequestSerializer(serializers.Serializer):
    """Enforces content schemas for deployment deactivation requests."""

    identifier = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=64)


class HeartBeatRequestSerializer(serializers.Serializer):
    """Enforces content schemas for heartbeat requests."""

    uuid = serializers.UUIDField()
    token = serializers.CharField(max_length=64)


class ValidateRequestSerializer(serializers.Serializer):
    """Enforces content schemas for token validation requests."""

    token = serializers.CharField(max_length=64)