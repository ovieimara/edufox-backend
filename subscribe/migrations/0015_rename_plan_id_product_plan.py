# Generated by Django 4.1.6 on 2023-05-30 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0014_product_plan_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='plan_id',
            new_name='plan',
        ),
    ]
