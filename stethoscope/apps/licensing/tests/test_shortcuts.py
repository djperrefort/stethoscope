"""Unit tests for the `shortcuts` module."""

from django.test import RequestFactory, TestCase

from stethoscope.apps.licensing.shortcuts import hash_token, resolve_client_ip


class ResolveClientIpFunction(TestCase):
    """Unit tests for the `resolve_client_ip` function."""

    def setUp(self) -> None:
        """Create test fixtures using mock data."""

        self.factory = RequestFactory()

    def test_returns_remote_addr_when_no_forwarded_headers(self) -> None:
        """Verify REMOTE_ADDR is returned when no proxy headers are present."""

        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        request.META.pop('HTTP_X_FORWARDED_FOR', None)
        request.META.pop('HTTP_X_REAL_IP', None)

        result = resolve_client_ip(request)

        self.assertEqual(result, '10.0.0.1')

    def test_returns_x_forwarded_for_over_remote_addr(self) -> None:
        """Verify HTTP_X_FORWARDED_FOR takes priority over REMOTE_ADDR."""

        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.5'
        request.META['REMOTE_ADDR'] = '10.0.0.1'

        result = resolve_client_ip(request)

        self.assertEqual(result, '203.0.113.5')

    def test_returns_x_real_ip_over_remote_addr(self) -> None:
        """Verify HTTP_X_REAL_IP takes priority over REMOTE_ADDR."""

        request = self.factory.get('/')
        request.META.pop('HTTP_X_FORWARDED_FOR', None)
        request.META['HTTP_X_REAL_IP'] = '198.51.100.9'
        request.META['REMOTE_ADDR'] = '10.0.0.1'

        result = resolve_client_ip(request)

        self.assertEqual(result, '198.51.100.9')

    def test_returns_x_forwarded_for_over_x_real_ip(self) -> None:
        """Verify HTTP_X_FORWARDED_FOR takes priority over HTTP_X_REAL_IP."""

        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.5'
        request.META['HTTP_X_REAL_IP'] = '198.51.100.9'

        result = resolve_client_ip(request)

        self.assertEqual(result, '203.0.113.5')

    def test_returns_leftmost_ip_from_comma_separated_forwarded_for(self) -> None:
        """Verify the original client IP is extracted from a forwarded-for chain."""

        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.5, 10.0.0.2, 10.0.0.3'

        result = resolve_client_ip(request)

        self.assertEqual(result, '203.0.113.5')

    def test_strips_whitespace_from_extracted_ip(self) -> None:
        """Verify leading and trailing whitespace is stripped from the result."""

        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '  203.0.113.5  , 10.0.0.2'

        result = resolve_client_ip(request)

        self.assertEqual(result, '203.0.113.5')

    def test_skips_empty_forwarded_for_and_falls_through(self) -> None:
        """Verify an empty HTTP_X_FORWARDED_FOR causes fallthrough to the next header."""

        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '   '
        request.META['HTTP_X_REAL_IP'] = '198.51.100.9'

        result = resolve_client_ip(request)

        self.assertEqual(result, '198.51.100.9')

    def test_returns_fallback_ip_when_all_headers_absent(self) -> None:
        """Verify the zero-address fallback is returned when no META headers are set."""

        request = self.factory.get('/')
        request.META.pop('HTTP_X_FORWARDED_FOR', None)
        request.META.pop('HTTP_X_REAL_IP', None)
        request.META.pop('REMOTE_ADDR', None)

        result = resolve_client_ip(request)

        self.assertEqual(result, '0.0.0.0')


class HashTokenFunction(TestCase):
    """Unit tests for the `hash_token` function."""

    def setUp(self) -> None:
        """Create test fixtures using mock data."""

        self.factory = RequestFactory()

    def test_returns_64_character_hex_string(self) -> None:
        """Verify the returned digest is a 64-character lowercase hex string."""

        result = hash_token('some-token')

        self.assertEqual(len(result), 64)
        self.assertRegex(result, r'^[0-9a-f]+$')

    def test_same_input_produces_same_digest(self) -> None:
        """Verify hashing is deterministic for identical inputs."""

        self.assertEqual(hash_token('some-token'), hash_token('some-token'))

    def test_different_inputs_produce_different_digests(self) -> None:
        """Verify distinct inputs do not collide."""

        self.assertNotEqual(hash_token('token-a'), hash_token('token-b'))

    def test_returns_known_digest_for_fixed_input(self) -> None:
        """Verify the output matches the expected SHA-256 digest for a known value."""

        result = hash_token('abc123')

        self.assertEqual(result, '6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090')
