from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.response import Response

from discordbot.startup import start_bot

class BotView(APIView):
    """ A view to provide an execution context for the unseen servant to reside in """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """ Launch the bot if not already running """
        try:
            start_bot()
        except Exception as e:
            print(e)
        finally:
            return Response({"message": "Bot started"}, status=HTTP_200_OK)
