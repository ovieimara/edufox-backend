# Generated by Django 4.1.6 on 2023-11-03 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0061_thumbnailurl_remove_thumbnail_urls'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ThumbnailURL',
        ),
    ]
