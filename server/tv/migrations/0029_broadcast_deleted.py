# Generated by Django 3.2.18 on 2023-03-21 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tv', '0028_alter_tv_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcast',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
