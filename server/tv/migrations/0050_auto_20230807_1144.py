# Generated by Django 4.0 on 2023-08-07 08:44

from django.db import migrations

def resave_spots_and_assets(apps, schema_editor):
    Spot = apps.get_model('tv', 'Spot')
    Asset = apps.get_model('tv', 'Asset')
    for spot in Spot.objects.all():
        spot.save()
    for asset in Asset.objects.all():
        asset.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tv', '0049_spot_name'),
    ]

    operations = [
        migrations.RunPython(resave_spots_and_assets, reverse_code=migrations.RunPython.noop),
    ]
