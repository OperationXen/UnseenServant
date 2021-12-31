from datetime import datetime
from asgiref.sync import sync_to_async

from core.models.game import Ban


@sync_to_async
def get_outstanding_bans():
    now = datetime.now()
    queryset = Ban.objects.filter(datetime_end__gte=now)
    return list(queryset)       # force evaluation before leaving this async context
