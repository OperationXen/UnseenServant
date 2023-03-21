
from rest_framework.views import Response, Request, APIView
from rest_framework.status import *


class StatusViewSet(APIView):
    """Views for server status """

    def get(self, request: Request):
        """ Get current status """

        return Response({'message': "This was a triumph, I'm making a note here - 'Huge success', It's hard to overstate my satisfaction", "status": "still alive"}, status=HTTP_200_OK)
