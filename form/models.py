from django.db import models

# Create your models here.


class Waiter(models.Model):
    first_name = models.CharField(
        db_index=True, max_length=255, null=True, blank=True, default="")
    last_name = models.CharField(
        db_index=True, max_length=255, null=True, blank=True, default="")
    email = models.EmailField(null=True, blank=True, default="")
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
