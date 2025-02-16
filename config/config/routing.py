from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.reports.routing  # Import reports WebSocket routes

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.reports.routing.websocket_urlpatterns  # Add reports WebSocket URLs
        )
    ),
})
