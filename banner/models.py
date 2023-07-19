from django.db import models

# Create your models here.


class Banner(models.Model):
    label = models.CharField(max_length=255, blank=True, null=True, default='')
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    url = models.URLField(null=True, blank=True, default='')
    dimensions = models.CharField(max_length=255, default='')
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.name if self.name else self.url}"
