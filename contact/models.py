from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    phone_number = models.CharField(max_length=15, null=False,
                                    default='', unique=True)
    email = models.EmailField(null=False,
                              default='', unique=True)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.phone_number}"


class ContactForm(models.Model):
    phone_number = models.CharField(max_length=15, null=False,
                                    default='', unique=True)
    email = models.EmailField(null=False,
                              default='', unique=True)
    message = models.TextField(null=False,
                               default='', unique=True)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.phone_number}"
