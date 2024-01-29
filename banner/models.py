from django.db import models

# Create your models here.


class Banner(models.Model):
    num = models.SmallIntegerField(null=True, blank=True, default=0)
    label = models.CharField(max_length=255, blank=True, null=True, default='')
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    url = models.URLField(null=True, blank=True, default='')
    dimensions = models.CharField(max_length=255, default='')
    text = models.CharField(max_length=255, null=True, blank=True, default='')
    description = models.TextField(null=True, blank=True, default='')
    discountPercentage = models.CharField(
        max_length=15, null=True, blank=True, default='')
    firstGradientColor = models.CharField(
        max_length=15, null=True, blank=True, default='')
    secondGradientColor = models.CharField(
        max_length=15, null=True, blank=True, default='')
    thirdGradientColor = models.CharField(
        max_length=15, null=True, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.name if self.name else self.url}"
