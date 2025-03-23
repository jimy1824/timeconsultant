from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians
from django.db.models import F


def get_ranking(ranking_type, institute):
    ranking = institute.instituteranking_set.filter(ranking_type=ranking_type).first()
    if ranking:
        return ranking.value
    else:
        return 'N/A'


def get_distance(lat, lon):
    dlat = Radians(F('latitude') - lat)
    dlong = Radians(F('longitude') - lon)

    a = (Power(Sin(dlat / 2), 2) + Cos(Radians(lat))
         * Cos(Radians(F('latitude'))) * Power(Sin(dlong / 2), 2)
         )

    c = 2 * ATan2(Sqrt(a), Sqrt(1 - a))
    d = 6371 * c

    return d
