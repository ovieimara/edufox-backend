# Generated by Django 4.1.6 on 2023-05-22 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0004_gradepack_remove_subscribe_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribe',
            name='grade',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscription_grade_pack', to='subscribe.gradepack'),
        ),
    ]
