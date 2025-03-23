from django.http import HttpResponse
from constructor.resources import DisciplineResource


def export(request):
    person_resource = DisciplineResource()
    dataset = person_resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="persons.xls"'
    return response
