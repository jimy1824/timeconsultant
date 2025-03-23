from constructor.models import Specialization, Institute, InstituteCampus
from haystack import indexes
from datetime import datetime


class SpecializationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/scrapedcontent_text.txt")
    name = indexes.CharField(model_attr='heading')

    def get_model(self):
        return Specialization

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_at__lte=datetime.now())


class InstituteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/institutes_text.txt")
    institute_name = indexes.CharField(model_attr='institute_name')

    def get_model(self):
        return Institute

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_at__lte=datetime.now())


class InstituteCampusIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/institutes_text.txt")
    institute = indexes.CharField(model_attr='institute__institute_name')

    def get_model(self):
        return InstituteCampus

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_at__lte=datetime.now())
