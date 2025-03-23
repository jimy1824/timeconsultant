from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings

from time_consultants.settings import PAGE_SIZE


class ResultsSetPagination(PageNumberPagination):
    page_size = api_settings.PAGE_SIZE
    # page_size = PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
