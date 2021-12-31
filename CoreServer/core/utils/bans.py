from datetime import datetime
from asgiref.sync import sync_to_async


from core.models.game import Ban


@sync_to_async
def get_outstanding_bans():
    now = datetime.now()
    queryset = Ban.objects.filter(datetime_end__gte=now)
    data = queryset.values_list('discord_name', 'datetime_end', 'variant', 'reason')
    len(data)       # force evaluation before leaving this async context
    return data