"""Exposes a callable ASGI entrypoint called `application`."""

from django.conf import settings
from django.core.asgi import get_asgi_application
from servestatic import ServeStaticASGI

application = get_asgi_application()
application = ServeStaticASGI(application, root=settings.STATIC_ROOT)
