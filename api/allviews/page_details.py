from rest_framework import viewsets, renderers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from constructor import models
from api.serializers import pages_details


class PagesDetailViewSet(viewsets.ModelViewSet):
    queryset = models.PagesDetailsContent.objects.all().order_by('category')
    serializer_classes = {
        'retrieve': pages_details.PageDetailSerializer,
    }
    default_serializer_class = pages_details.PageDetailSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], name='category', url_path='category/(?P<category>[A-Za-z0-9-]+)')
    def category(self, request, category, *args, **kwargs):
        qs = models.PagesDetailsContent.objects.filter(category=category).first()
        serializer = self.get_serializer(qs)
        return Response(serializer.data)
