from auditlog.models import LogEntry
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView, TemplateView


class IndexView(TemplateView):
    template_name = "index.html"


class ObjectHistoryView(LoginRequiredMixin, ListView):
    """Render the auditlog history for any registered model instance."""

    template_name = "audit_history.html"
    context_object_name = "log_entries"
    paginate_by = 25

    def get_queryset(self):
        app_label = self.kwargs["app_label"]
        model_name = self.kwargs["model_name"]
        pk = self.kwargs["pk"]
        self._model_class = apps.get_model(app_label, model_name)
        ct = ContentType.objects.get_for_model(self._model_class)
        return LogEntry.objects.filter(content_type=ct, object_pk=str(pk)).order_by(
            "-timestamp"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_verbose_name"] = self._model_class._meta.verbose_name
        context["object_pk"] = self.kwargs["pk"]
        return context
