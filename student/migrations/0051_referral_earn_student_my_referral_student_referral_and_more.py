# Generated by Django 4.1.6 on 2023-10-11 17:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0050_remove_student_referrals_student_referral_code'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='referral',
        #     name='earn',
        #     field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referral_earning', to='student.earn'),
        # ),
        # migrations.AddField(
        #     model_name='student',
        #     name='my_referral',
        #     field=models.CharField(blank=True, db_index=True, default='', max_length=255, null=True),
        # ),
        # migrations.AddField(
        #     model_name='student',
        #     name='referral',
        #     field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referral_student', to='student.referral'),
        # ),
        migrations.AlterField(
            model_name='student',
            name='image_url',
            field=models.URLField(blank=True, default='', null=True),
        ),
    ]
