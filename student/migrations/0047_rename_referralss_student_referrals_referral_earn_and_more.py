# Generated by Django 4.1.6 on 2023-10-11 16:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0046_rename_referrals_student_referralss_referral_earn_and_more'),
    ]

    operations = [
        # migrations.RenameField(
        #     model_name='student',
        #     old_name='referralss',
        #     new_name='referrals',
        # ),
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
    ]
