import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View

from constructor.models import (Country, Institute, Discipline, Specialization, Course, Scholarship, InstituteCampus)
from common.utils import update_type
from functools import partial
from common import constants
from django.contrib.auth.decorators import login_required


# Create your views here.
class Home(View):
    template_name = 'home.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})


class InstitutesView(View):
    template_name = 'search_result.html'

    def post(self, request, *args, **kwargs):
        if request.POST.get('categories'):
            query = eval(request.POST.get('categories'))
            location = request.POST.get('location')
            if query.get('type') == 'institute':
                result = Institute.objects.filter(name=query.get('name'))
            if query.get('type') == 'course':
                result = Course.objects.filter(name=query.get('name'))
            if query.get('type') == 'discipline':
                result = Course.objects.filter(discipline__name=query.get('name'))
            if query.get('type') == 'specilization':
                result = Course.objects.filter(discipline__name=query.get('name'))

        # query = Course.objects.all()
        # if request.POST.get('institute'):
        #     query = query.filter(name=request.POST.get('course'))
        # if request.POST.get('country'):
        #     query = query.filter(institute__country=request.POST.get('country'))
        # if request.POST.get('discipline'):
        #     query = query.filter(discipline__name=request.POST.get('discipline'))
        # serializer_cls = self.get_serializer_class()
        # serializer = serializer_cls(query, many=True)
        # institutes_ids = query.values_list('institute', flat=True).distinct()
        # institutes = Institute.objects.filter(id__in=institutes_ids)
        # locations = []
        # for institute in institutes:
        #     institute_card = render_to_string('courses_map_view.html',
        #                                       {'institute': institute})
        #     locations.append({'lat': institute.lat, 'lng': institute.lng, 'card': institute_card})
        # #
        # # rendered = render_to_string('search_results.html',
        # #                             {'results': serializer.data, 'map_locations': locations})
        return render(request, self.template_name, context={'results': result})


def course_autocomplete(request):
    if request.is_ajax():
        query = request.GET.get("term", "")
        courses = Course.objects.filter(name__icontains=query)
        results = []
        for course in courses:
            results.append({'id': course.id, 'text': course.name})
        data = json.dumps({"results": results})

    mimetype = "application/json"
    return HttpResponse(data, mimetype)


def autocomplete(request):
    if 'term' in request.GET:
        qs = Course.objects.filter(name__icontains=request.GET.get('term'))
        titles = list()
        for product in qs:
            titles.append(product.cat_name)
            # titles = [product.title for product in qs]
        return JsonResponse(titles, safe=False)
    return render(request, 'home.html')
