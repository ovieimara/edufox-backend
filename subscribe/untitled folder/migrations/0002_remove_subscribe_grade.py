# Generated by Django 4.1.6 on 2023-03-27 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscribe',
            name='grade',
        ),
    ]
