"""Exposes a callable ASGI entrypoint called `application`."""

import os

from django.conf import settings
from django.core.asgi import get_asgi_application
from servestatic import ServeStaticASGI

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stethoscope.main.settings')

application = get_asgi_application()
application = ServeStaticASGI(application, root=settings.STATIC_ROOT)
