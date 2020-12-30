from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/workflows/(?P<wid>\w+)/$",
        consumers.WorkflowConsumer.as_asgi(),
        name="workflow_status_websocket",
    ),
]

app_name = "main"
