from django.urls import path 
from . import consumers

websocket_urlpatterns = [
    path('ws/socket-server/<uuid:uid>', consumers.ChatConsumer.as_asgi())
]