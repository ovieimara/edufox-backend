# Generated by Django 4.1.6 on 2023-05-06 16:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assess', '0008_alter_assessment_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to=settings.AUTH_USER_MODEL),
        ),
    ]
