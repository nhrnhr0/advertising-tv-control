def convert_broadcast_in_tvs_to_spot(apps, schema_editor):
    Spot = apps.get_model('tv', 'Spot')
    bInTv = apps.get_model('tv', 'BroadcastInTvs')
    Asset = apps.get_model('tv', 'Asset')
    
    for broadcast_in_tvs in bInTv.objects.all():
        is_filler = broadcast_in_tvs.master
        if broadcast_in_tvs.activeSchedule:
            is_active_toggel = broadcast_in_tvs.activeSchedule.is_active_var
        else:
            is_active_toggel = False
        filler_duration = broadcast_in_tvs.duration
        publisher = broadcast_in_tvs.broadcast.publisher
        # load assets
        # media
        # media_type
        media = broadcast_in_tvs.broadcast.media
        media_type = broadcast_in_tvs.broadcast.media_type
        tvs = broadcast_in_tvs.tvs
        
        spot = Spot.objects.create(is_filler=is_filler, is_active_toggel=is_active_toggel, filler_duration=filler_duration, publisher=publisher)
        spot.tvs.set(tvs.all())
        # adding the assets
        # create new Asset
        asset = Asset(media=media, media_type=media_type)
        # add the asset to the spot
        spot.assets.add(asset)
        # save the spot
        spot.save()
