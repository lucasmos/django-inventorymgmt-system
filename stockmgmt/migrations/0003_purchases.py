# Generated by Django 5.0.3 on 2024-04-10 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0002_supplier_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchases',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_code', models.CharField(max_length=100)),
                ('quantity_supplied', models.PositiveIntegerField(blank=True, default='0', null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.category')),
                ('product_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.products')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.supplier')),
            ],
        ),
    ]