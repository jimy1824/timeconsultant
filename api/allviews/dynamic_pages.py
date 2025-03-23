from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from constructor.paginator import ResultsSetPagination
from rest_framework import viewsets
from constructor import models
from api.serializers import dynamic_pages
from rest_framework.response import Response


class DynamicPagesView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.DynamicPages.objects.filter(active=True)
    serializer_classes = {
        'list': dynamic_pages.DynamicPagesListSerializer,
        'retrieve': dynamic_pages.DynamicPagesDetailSerializer,
        'type_respective_page': dynamic_pages.DynamicPagesDetailSerializer,
    }
    default_serializer_class = dynamic_pages.DynamicPagesListSerializer
    pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], name='type_respective_page',
            url_path='type/(?P<page_type>[\w:|-]+)/detail')
    def type_respective_page(self, request, page_type, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        page = get_object_or_404(models.DynamicPages, type=page_type)
        serializer = self.get_serializer(page)
        return Response(serializer.data)
