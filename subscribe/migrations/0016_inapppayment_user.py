# Generated by Django 4.1.6 on 2023-09-03 13:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscribe', '0015_rename_plan_id_product_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='inapppayment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_in_apps_payment', to=settings.AUTH_USER_MODEL),
        ),
    ]
