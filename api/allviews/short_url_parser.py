from rest_framework import viewsets
from rest_framework import status
from constructor import models
from api.serializers import short_url_serializer
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid


def generate_uuid():
    uid = ''
    while 1 > 0:
        uid = str(uuid.uuid4())
        if not models.ShortUrl.objects.filter(uuid=uid).exists():
            break
    return uid


class ShortUrlView(viewsets.ModelViewSet):
    queryset = models.ShortUrl.objects.all()
    serializer_classes = {
        'retrieve': short_url_serializer.ShortUrlRetrieveSerializer,
        'search_uuid': short_url_serializer.ShortUrlRetrieveSerializer,
        'post': short_url_serializer.ShortUrlRetrieveSerializer,
    }
    default_serializer_class = short_url_serializer.ShortUrlRetrieveSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['uuid'] = generate_uuid()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], name='search_uuid',url_path='uuid/(?P<uuid>[A-Za-z0-9-]+)')
    def search_uuid(self, request, uuid, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        print('lkkkkk','uuid')
        qs = get_object_or_404(models.ShortUrl, uuid=uuid)
        serializer = self.get_serializer(qs)
        return Response(serializer.data)
