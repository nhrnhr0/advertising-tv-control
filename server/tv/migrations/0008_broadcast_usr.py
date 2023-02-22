# Generated by Django 4.1.6 on 2023-02-21 09:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tv', '0007_alter_playedbroadcast_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcast',
            name='usr',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
