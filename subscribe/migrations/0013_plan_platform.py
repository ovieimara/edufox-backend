# Generated by Django 4.1.6 on 2023-05-30 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0012_alter_product_product_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='platform',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
