# Generated by Django 4.1.6 on 2023-03-29 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_alter_student_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tempstudent',
            name='last_updated',
        ),
    ]
