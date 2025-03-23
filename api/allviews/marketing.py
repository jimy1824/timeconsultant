from constructor.paginator import ResultsSetPagination
from rest_framework import viewsets
from constructor import models
from api.serializers import marketing
from rest_framework.decorators import action
from rest_framework.response import Response


class MarketingCardView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.MarketingCard.objects.filter(active=True)
    serializer_classes = {
        'list': marketing.MarketingListSerializer,
        'retrieve': marketing.MarketingDetailSerializer,
    }
    default_serializer_class = marketing.MarketingListSerializer
    pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

