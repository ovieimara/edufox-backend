# Generated by Django 4.1.6 on 2023-03-27 07:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        # ('course', '0019_rename_video_time_of_interaction_interaction_duration_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, null=True)),
                ('value', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('symbol', models.CharField(default=True, max_length=127, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InAppPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, null=True)),
                ('environment', models.CharField(default='', max_length=255, null=True)),
                ('original_transaction_id', models.CharField(default='', max_length=255, null=True)),
                ('transaction_id', models.CharField(default='', max_length=255, null=True)),
                ('posix_date_time', models.CharField(default='', max_length=255, null=True)),
                ('expires_date', models.CharField(default='', max_length=255, null=True)),
                ('original_transaction_id2', models.CharField(default='', max_length=255, null=True)),
                ('auto_renew_status', models.CharField(default='', max_length=255, null=True)),
                ('expiration_intent', models.CharField(default='', max_length=255, null=True)),
                ('in_app_ownership_type', models.CharField(default='', max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100, null=True)),
                ('amount', models.IntegerField()),
                ('currency', models.CharField(default='=N=', max_length=15, null=True)),
                ('description', models.TextField(default='', null=True)),
                ('duration', models.SmallIntegerField(default=0)),
                ('discount', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discounts', to='subscribe.discount')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, null=True)),
                ('product_id', models.CharField(default='', max_length=255, null=True)),
                ('platform', models.CharField(default='', max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True, null=True)),
                ('grade', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscription_grade', to='course.grade')),
                ('payment', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gateways', to='subscribe.inapppayment')),
                ('plan', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plans', to='subscribe.plan')),
                ('user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='inapppayment',
            name='product',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='subscribe.product'),
        ),
    ]
