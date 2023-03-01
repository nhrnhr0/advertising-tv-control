from django.shortcuts import redirect, render
from tv.models import Broadcast,Tv,BroadcastQrScaned
def qr_scaned(request,tv_id, broadcast_id):
    print('qr_scaned: ', broadcast_id)
    broadcast = Broadcast.objects.get(id=broadcast_id)
    print('broadcast: ', broadcast)
    tv = Tv.objects.get(id=tv_id)
    save_broadcast_scaned(tv, broadcast)
    link = broadcast.qr_link
    if not link:
        link = broadcast.publisher.qr_link
    return redirect()

def save_broadcast_scaned(tv, broadcast):
    print('save_broadcast_scaned: ', broadcast)
    broadcast_qr_scaned = BroadcastQrScaned.objects.create(
        tv=tv,
        broadcast=broadcast,
        link=broadcast.qr_link
    )
    broadcast_qr_scaned.save()
    return broadcast_qr_scaned