from import_export import resources
from constructor import models
from import_export import fields, widgets


# Discipline
# DegreeLevel
# CourseTitle
# PathwayGroup
# InstituteGroup
# Currency


class InstituteResource(resources.ModelResource):
    class Meta:
        model = models.Institute


class DisciplineResource(resources.ModelResource):
    class Meta:
        model = models.Discipline


class DegreeLevelResource(resources.ModelResource):
    class Meta:
        model = models.DegreeLevel


class CourseTitleResource(resources.ModelResource):
    class Meta:
        model = models.CourseTitle


class PathwayGroupResource(resources.ModelResource):
    class Meta:
        model = models.PathwayGroup


class InstituteGroupResource(resources.ModelResource):
    class Meta:
        model = models.InstituteGroup


class CurrencyResource(resources.ModelResource):
    class Meta:
        model = models.Currency

# class CourseResource(resources.ModelResource):
#     discipline = fields.Field( widget=widgets.ForeignKeyWidget(models.Discipline))
#     course_title = fields.Field( widget=widgets.ForeignKeyWidget(models.CourseTitle))
#     degree_level = fields.Field( widget=widgets.ForeignKeyWidget(models.DegreeLevel))
#     specialization = fields.Field( widget=widgets.ForeignKeyWidget(models.Specialization))
#     class Meta:
#         model = models.Course
#
#     def before_row_import(self, row, **kwargs):
#         import pdb;pdb.set_trace()
#         for key in row.keys():
#             print(row[key])
#         # if "warn" in row.keys():
#         #     # munge "warn" to "True"
#         #     if row["warn"] in ["warn", "WARN"]:
#         #         row["warn"] = True
#
#         return super().before_import_row(row, **kwargs)
