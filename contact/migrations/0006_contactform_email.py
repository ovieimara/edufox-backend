# Generated by Django 4.1.6 on 2023-11-22 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0005_alter_contactform_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactform',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
    ]
