"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings.prod")

django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from pi import routing
from channels.routing import URLRouter

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
                 URLRouter(routing.websocket_urlpatterns)
        )
    })