# Generated by Django 4.1.6 on 2023-05-05 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assess', '0002_alter_test_lesson_alter_test_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='question',
            field=models.TextField(default=''),
        ),
    ]
