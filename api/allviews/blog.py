from constructor.paginator import ResultsSetPagination
from rest_framework import viewsets
from constructor import models
from api.serializers import blog


class BlogView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.Blog.objects.all().order_by('updated_at')
    serializer_classes = {
        'list': blog.BlogListSerializer,
        'retrieve': blog.BlogDetailSerializer,
    }
    default_serializer_class = blog.BlogListSerializer
    pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)
