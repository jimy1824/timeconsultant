from collections import defaultdict
import json
from django.http import HttpResponse
from django.db.models import Count, QuerySet
from rest_framework import viewsets, renderers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from constructor import models
from api.serializers import top_words_serializer


class TopWordsViewSet(viewsets.ModelViewSet):
    queryset = models.TopKeyWords.objects.all().order_by('word')
    serializer_classes = {
        'list': top_words_serializer.TopKeyWordSerializer,
        'retrieve': top_words_serializer.TopKeyWordSerializer,
    }
    default_serializer_class = top_words_serializer.TopKeyWordSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], name='all', url_path='all')
    def all(self, request, *args, **kwargs):
        """
        Returns  institutes list by country id with count`.
        """
        serializer = self.get_serializer(models.TopKeyWords.objects.all().order_by('word'), many=True)
        return Response(serializer.data)


