# Generated by Django 4.1.6 on 2023-11-21 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0072_lesson_is_active_subtopic_chapter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subtopic',
            name='subject',
        ),
        migrations.DeleteModel(
            name='Chapter',
        ),
        migrations.DeleteModel(
            name='SubTopic',
        ),
    ]
