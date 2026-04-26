#!/usr/bin/env python
"""Command-line utility for executing administrative tasks."""

import os
import sys

from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stethoscope.main.settings')


def main() -> None:  # pragma: nocover
    """Parse the commandline and run administrative tasks."""

    # Override version value
    if '--version' in sys.argv:
        from django.conf import settings
        print(settings.VERSION)
        sys.exit(0)

    execute_from_command_line(sys.argv)


if __name__ == '__main__':  # pragma: nocover
    main()
