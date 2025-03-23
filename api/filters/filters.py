import django_filters
from constructor import models as appModels


class CourseNameFilter(django_filters.FilterSet):
    class Meta:
        model = appModels.Course
        fields = ['username', 'first_name', 'last_name', ]
