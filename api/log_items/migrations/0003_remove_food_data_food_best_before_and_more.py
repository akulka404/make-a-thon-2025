# Generated by Django 5.1.5 on 2025-01-25 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log_items', '0002_alter_food_data_food_usage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food_data',
            name='food_best_before',
        ),
        migrations.AlterField(
            model_name='food_data',
            name='expired_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='food_data',
            name='expired_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='food_data',
            name='stored_date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='food_data',
            name='stored_time',
            field=models.TimeField(auto_now_add=True),
        ),
    ]
