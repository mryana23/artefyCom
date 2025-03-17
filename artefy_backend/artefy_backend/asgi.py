import os
import django

# Set Django settings module before doing anything else
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artefy_backend.settings")

# Setup Django
django.setup()

# Now import the rest after Django is configured
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
import chat.routing

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        )
    ),
})