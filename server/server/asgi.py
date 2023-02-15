"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter


django_asgi_app = get_asgi_application()


from channels.auth import AuthMiddlewareStack
import pi.routing



# application = get_asgi_application()
application = ProtocolTypeRouter({
    'http':django_asgi_app,
    'websocket':AuthMiddlewareStack(
        URLRouter(
            pi.routing.websocket_urlpatterns
        )
    )
})

