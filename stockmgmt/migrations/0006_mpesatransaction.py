# Generated by Django 5.0.3 on 2024-05-02 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0005_remove_purchases_category_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='MPesaTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15, verbose_name='Phone Number')),
                ('amount', models.IntegerField(verbose_name='Amount')),
                ('account_reference', models.CharField(max_length=50, verbose_name='Account Reference')),
                ('transaction_desc', models.CharField(max_length=255, verbose_name='Transaction Description')),
            ],
            options={
                'verbose_name': 'M-Pesa Transaction',
                'verbose_name_plural': 'M-Pesa Transactions',
            },
        ),
    ]
