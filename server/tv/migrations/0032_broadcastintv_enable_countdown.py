# Generated by Django 4.0 on 2023-03-25 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tv', '0031_alter_tv_buisness_types_alter_tv_not_to_show_list_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcastintv',
            name='enable_countdown',
            field=models.BooleanField(default=True),
        ),
    ]
