"""Serializers for parsing and validating HTTP request content."""

from rest_framework import serializers

__all__ = [
    'HeartBeatRequestSerializer',
    'ValidateRequestSerializer',
]


class ValidateRequestSerializer(serializers.Serializer):
    """Enforces content schemas for token validation requests."""

    token = serializers.CharField(max_length=64)


class HeartBeatRequestSerializer(serializers.Serializer):
    """Enforces content schemas for heartbeat requests."""

    uuid = serializers.UUIDField()
    token = serializers.CharField(max_length=64)
