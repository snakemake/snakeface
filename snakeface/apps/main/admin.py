from django.contrib import admin
from snakeface.apps.main.models import Workflow


class WorkflowAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "add_date",
        "snakefile",
        "workdir",
    )

    fields = (
        "command",
        "data",
        "dag",
        "error",
        "output",
        "name",
        "snakefile",
        "snakemake_id",
        "status",
        "thread",
        "retval",
        "workdir",
        "owners",
        "contributors",
    )


admin.site.register(Workflow, WorkflowAdmin)
