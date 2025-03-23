from time_consultants.celery import app as celery_app
from constructor.models import Course, CourseFee, Currency
from constructor.choices import headers
import requests


@celery_app.task
def currency_base_values():
    response = requests.get(
        "http://api.exchangeratesapi.io/v1/latest?base=EUR&access_key=0cd5a12fe6261114d427d42aca1e2832")
    if response.status_code == 200:
        response = response.json()
        rates = response.get('rates')
        currencies = Currency.objects.all()
        for currency in currencies:
            pkr = float(rates.get('PKR'))
            if rates.get(currency.display_name.strip()):
                currency.value_to_pkr = pkr / float(rates.get(currency.display_name.strip()))
                currency.save()
            else:
                print(currency.display_name)



@celery_app.task
def currency_converter():
    courses = Course.objects.all()
    for num, course in enumerate(courses, start=1):
        print(num)
        fees = course.coursefee_set.all()
        duration = course.courseduration_set.first()
        if len(fees) >= 1:
            fee = fees.filter(type=headers.FEE_PER_YEAR).first()
            if fee:
                fee = fee.ceil_value * fee.currency.value_to_pkr
            elif fees.filter(type=headers.TOTAL_PATHWAY_FEE).first():
                fee = fees.filter(type=headers.TOTAL_PATHWAY_FEE).first()
                fee = fee / duration
            elif fees.filter(type=headers.DIRECT_ENTRY_FEE_PER_SEMESTER).first():
                fee = fees.filter(type=headers.DIRECT_ENTRY_FEE_PER_SEMESTER).first()
                fee = fee * 3
            if fee:
                print(fee, ' fee')
                course.base_fee = fee
                course.save()
        if len(fees) == 0:
                course.base_fee = None
                course.save()

