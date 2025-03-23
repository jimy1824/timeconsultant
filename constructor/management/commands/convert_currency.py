from django.core.management.base import BaseCommand, CommandError
from constructor.models import Course, CourseFee, Currency
from constructor.choices import headers
from common.tasks import currency_base_values, currency_converter


class Command(BaseCommand):
    help = 'Currency Coverted Successfully!'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        currency_converter.delay()
        self.stdout.write("task run successfully")
