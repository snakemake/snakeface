from django.conf.urls import url
from django.urls import path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from snakeface.settings import cfg
import snakeface.apps.api.views as api_views
from .permissions import AllowAnyGet

# Documentation URL
schema_view = get_schema_view(
    openapi.Info(
        title="SnakeFace API",
        default_version="v1",
        description="API for Snakemake to interact with Snakeface",
        license=openapi.License(name="Apache License"),
        contact=openapi.Contact(url=cfg.HELP_CONTACT_URL),
    ),
    public=True,
    permission_classes=(AllowAnyGet,),
)

urlpatterns = [
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
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
