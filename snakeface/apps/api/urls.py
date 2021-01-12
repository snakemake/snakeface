from django.conf.urls import url
from django.urls import path

from snakeface.settings import cfg
import snakeface.apps.api.views as api_views
from .permissions import AllowAnyGet

urlpatterns = [
    path(
        "api/service-info",
        api_views.ServiceInfo.as_view(),
        name="service_info",
    ),
    path(
        "create_workflow",
        api_views.CreateWorkflow.as_view(),
        name="create_workflow",
    ),
    path(
        "update_workflow_status",
        api_views.UpdateWorkflow.as_view(),
        name="update_workflow_status",
    ),
]


app_name = "api"
