# ruff: noqa: N999, I001

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "BlockingEngine.Config.Settings",
)


application = get_asgi_application()