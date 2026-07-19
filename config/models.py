"""Shared model conventions.

Domain models should extend ``BaseModel`` (or ``UUIDTimeStampedModel`` when
soft deletion isn't wanted). ``objects`` returns ALL rows — there is no hidden
default filtering — so querysets opt in explicitly:

    class ThingViewSet(ModelViewSet):
        def get_queryset(self):
            return Thing.objects.alive()

DRF's stock ``destroy()`` calls ``instance.delete()``, which soft-deletes.
"""

import uuid

from django.db import models
from django.utils import timezone


class UUIDTimeStampedModel(models.Model):
    """UUIDv7 primary key (time-ordered, safe to expose) plus timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class BaseModel(UUIDTimeStampedModel):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)
