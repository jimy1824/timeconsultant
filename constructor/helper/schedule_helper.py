from datetime import datetime
from constructor.helper import headers
from constructor import models, forms


# from constructor.helper.import_course_data import parse_error

def parse_error(errors, row):
    return [{'key': k, 'error': v[0] + ' row number is ' + str(row)} for k, v in errors.items()]


def create_or_update_admission_schedule(data, course, row):
    # intake must be given if not course intake deadline  will be empty
    intakes_data = data.get(headers.INTAKE)
    deadlines_data = data.get(headers.DEADLINE)
    application_dates_data = data.get(headers.APPLICATION_OPEN_DATE)
    if intakes_data:
        if not isinstance(intakes_data, str):
            return False, [{'key': headers.INTAKE,
                            'error': '' + str(
                                intakes_data) + 'not valid format  (excel date will not be accepted )  in  '
                                                'row number ' + str(
                                row)}]
        intakes_data = intakes_data.strip()
    if deadlines_data:
        if not isinstance(deadlines_data, str):
            return False, [{'key': headers.DEADLINE,
                            'error': '' + str(
                                deadlines_data) + 'not valid format  (excel date will not be accepted)  in '
                                                  'row '
                                                  'number is ' + str(
                                row)}]
        deadlines_data = deadlines_data.strip()
    if application_dates_data:
        if not isinstance(deadlines_data, str):
            return False, [{'key': headers.DEADLINE,
                            'error': '' + str(
                                deadlines_data) + ' not valid format  (excel date will not be accepted)  in row '
                                                  'number is ' + str(
                                row)}]
        application_dates_data = application_dates_data.strip()

    if intakes_data:
        if intakes_data == 'rolling_admissions':
            return get_update_create_intake_rolling(course, row)
        if application_dates_data:
            if deadlines_data:
                return get_update_create_intake_deadline_application_open_date(
                    intakes_data, deadlines_data, application_dates_data, course,
                    row)


            else:
                return False, [{'key': headers.DEADLINE,
                                'error': '' + headers.APPLICATION_OPEN_DATE + ' is  given but ' + headers.DEADLINE + ' is not given in row number  ' + str(
                                    row)}]

        elif deadlines_data:
            if intakes_data and deadlines_data == 'rolling_admissions':
                return get_update_create_rolling_admission(intakes_data, course, row)

            else:
                return get_update_create_intakes_deadlines(intakes_data, deadlines_data, course, row)
        else:
            return get_update_create_intakes(intakes_data, course, row)

    else:
        return False, [{'key': headers.INTAKE, 'error': 'Intake is required row number is ' + str(row)}]
    return True, None


# save or update schedule
def save_course_schedule(data, course, row):
    form = forms.CourseIntakeAndDeadLineForm(data, initial={'course': course})
    if form.is_valid():
        form_data = form.cleaned_data
        if models.CourseIntakeAndDeadLine.objects.filter(course__id=course.id,
                                                         intake_month=form_data.get('intake_month')
                                                         ).exists():
            models.CourseIntakeAndDeadLine.objects.filter(course__id=course.id,
                                                          intake_month=form_data.get('intake_month')
                                                          ).update(**form_data)
        else:
            form.save()

        # course_intake, status = models.CourseIntakeAndDeadLine.objects.update_or_create(
        #     course=form_data.get('course'),
        #     intake_month=form_data.get('intake_month'),
        #     defaults=form_data)
        return True, None

    else:
        errors = parse_error(form.errors, row)
        return False, errors


# zero case
def get_update_create_intake_rolling(course, row):
    data = {'course': course, 'rolling_intake': True, 'rolling_deadline': True}
    course_intake, status = models.CourseIntakeAndDeadLine.objects.update_or_create(
        course=course,
        rolling_intake=True,
        defaults=data)
    return True, None


# first case
def get_update_create_rolling_admission(intakes, course, row):
    intake_value_list = []
    intakes_list = intakes.split(',')
    intakes_list = list(filter(None, intakes_list))
    for intake in intakes_list:
        response = {}
        intake_status, intake_response = get_date(intake)
        if not intake_status:
            return False, [{'key': headers.INTAKE,
                            'error': '' + intake_response + ' and row number is ' + str(row)}]
        response['intake_month'] = intake_response.get('month')
        response['intake_day'] = intake_response.get('days')
        response['intake_year'] = intake_response.get('year')
        intake_value_list.append(response)
    for intake in intake_value_list:
        intake['course'] = course
        intake['rolling_deadline'] = True
        course_intake, status = models.CourseIntakeAndDeadLine.objects.update_or_create(
            course=course,
            intake_month=intake.get('intake_month'),
            defaults=intake)
    return True, None


# second case only intakes are given
def get_intakes_list(intakes):
    dates_list = []
    intakes_list = intakes.split(',')
    intakes_list = list(filter(None, intakes_list))
    for date in intakes_list:
        date_status, date_response = get_date(date)
        if not date_status:
            return date_status, date_response
        dates_list.append({'intake_month': date_response.get('month'),
                           'intake_day': date_response.get('days'),
                           'intake_year': date_response.get('year')})
    return True, dates_list


def get_update_create_intakes(intakes, course, row):
    if intakes == "tbc":
        return True, None
    status, responses = get_intakes_list(intakes)
    if not status:
        return False, [{'key': headers.INTAKE,
                        'error': '' + intakes + ' must be in proper format ' + responses + ' and row number is ' + str(
                            row)}]
    for response in responses:
        update_status, update_response = save_course_schedule(response, course, row)
        if not update_status:
            return update_status, update_response
    return True, None


# third case  intakes and deadlines  are given

def get_intakes_deadline_list(intakes, deadlines, row):
    intakes_deadlines_list = []
    intakes_deadlines_values_list = []
    intakes_list = intakes.split(',')
    deadlines_list = deadlines.split(',')
    deadlines_list = list(filter(None, deadlines_list))
    intakes_list = list(filter(None, intakes_list))
    if len(intakes_list) == len(deadlines_list):
        length = len(intakes_list)
        for index in range(length):
            intakes_deadlines_list.append(
                {'intake': intakes_list[index].strip(), 'deadline': deadlines_list[index].strip()})
        for index in range(length):
            response = {}
            data = intakes_deadlines_list[index]
            if len(data.get('deadline')) > 3 and data.get('deadline') != 'tbc' and data.get('deadline') != 'TBC':
                deadline_status, deadline_response = get_date(data.get('deadline'))
                if not deadline_status:
                    return False, [{'key': headers.DEADLINE,
                                    'error': ''
                                             + deadline_response + ' date number ' + str(index) + ' and '
                                                                                                  ' row number is ' + str(
                                        row)}]
                response['deadline_day'] = deadline_response.get('days')
                response['deadline_months'] = deadline_response.get('month')
                response['deadline_year'] = deadline_response.get('year')

            intake_status, intake_response = get_date(data.get('intake'))
            if not intake_status:
                return False, [{'key': headers.DEADLINE,
                                'error': ''
                                         + intake_response + ' date number ' + str(index) + ' and '
                                                                                            ' row number is ' + str(
                                    row)}]
            response['intake_month'] = intake_response.get('month')
            response['intake_day'] = intake_response.get('days')
            response['intake_year'] = intake_response.get('year')
            intakes_deadlines_values_list.append(response)
        return True, intakes_deadlines_values_list

    else:
        return False, [{'key': headers.INTAKE,
                        'error': ' numbers of entries are not equal'
                                 + headers.INTAKE + ' are ' + str(len(intakes_list)) + ' and '
                                 + headers.DEADLINE + ' are ' + str(len(deadlines_list)) +
                                 ' row number is ' + str(
                            row)}]


def get_update_create_intakes_deadlines(intakes, deadlines, course, row):
    intakes_deadline_status, intakes_deadlines_responses = get_intakes_deadline_list(intakes, deadlines, row)
    if not intakes_deadline_status:
        return intakes_deadline_status, intakes_deadlines_responses

    if len(intakes_deadlines_responses):
        for intakes_deadline_response in intakes_deadlines_responses:
            update_status, update_response = save_course_schedule(intakes_deadline_response, course, row)
            if not update_status:
                return update_status, update_response

    else:
        return False, [{'key': headers.INTAKE + ' and ' + headers.DEADLINE,
                        'error': '' + intakes + ' and ' + deadlines + ' must be in proper format  and row number is ' + str(
                            row)}]

    return True, None


# fourth case  intakes and deadlines  are given

def get_intakes_deadline_application_open_dates_list(intakes, deadlines, application_open_dates, row):
    dates_list = []
    dates_updated_values_list = []
    intakes_list = intakes.strip().split(',')
    deadlines_list = deadlines.strip().split(',')
    application_open_dates_list = application_open_dates.strip().split(',')

    intakes_list = list(filter(None, intakes_list))
    deadlines_list = list(filter(None, deadlines_list))
    application_open_dates_list = list(filter(None, application_open_dates_list))

    if len(intakes_list) == len(deadlines_list) == len(application_open_dates_list):
        length = len(intakes_list)
        for index in range(length):
            dates_list.append({'intake': intakes_list[index].strip(), 'deadline': deadlines_list[index].strip(),
                               'open_date': application_open_dates_list[index].strip()})
        for index in range(length):
            response = {}
            data = dates_list[index]
            intake = data.get('intake').strip()
            deadline = data.get('deadline').strip()
            open_date = data.get('open_date').strip()
            #  get intakes
            intake_status, intake_response = get_date(intake)
            if not intake_status:
                return False, [{'key': headers.INTAKE,
                                'error': ''
                                         + intake_response + ' date number ' + str(index) + ' and '
                                                                                            ' row number is ' + str(
                                    row)}]
            response['intake_month'] = intake_response.get('month')
            response['intake_day'] = intake_response.get('days')
            response['intake_year'] = intake_response.get('year')
            # get deadlines
            if len(deadline) > 3 and deadline != 'tbc' and deadline != 'TBC':
                deadline_status, deadline_response = get_date(deadline)
                if not deadline_status:
                    return False, [{'key': headers.DEADLINE,
                                    'error': ''
                                             + deadline_response + ' date number in cell is ' + str(index + 1) + ' and '
                                                                                                                 'row '
                                                                                                                 'number is ' + str(
                                        row)}]
                response['deadline_day'] = deadline_response.get('days')
                response['deadline_months'] = deadline_response.get('month')
                response['deadline_year'] = deadline_response.get('year')

            # get applications open dates
            if len(open_date) > 3 and open_date != 'tbc' and open_date != 'TBC':
                open_dates_status, open_dates_response = get_date(open_date)
                if not open_dates_status:
                    return False, [{'key': headers.APPLICATION_OPEN_DATE,
                                    'error': ''
                                             + open_dates_response + ' date number in cell is ' + str(
                                        index + 1) + ' and '
                                                     ' row number is ' + str(
                                        row)}]

                response['application_open_day'] = open_dates_response.get('days')
                response['application_open_months'] = open_dates_response.get('month')
                response['application_open_year'] = open_dates_response.get('year')

            dates_updated_values_list.append(response)
        return True, dates_updated_values_list

    else:
        return False, [{'key': headers.INTAKE,
                        'error': ' numbers of entries are not equal '
                                 + headers.INTAKE + ' are ' + str(len(intakes_list)) + ' , '
                                 + headers.DEADLINE + ' are ' + str(len(deadlines_list)) + ' and '
                                 + headers.APPLICATION_OPEN_DATE + ' are ' + str(len(application_open_dates_list)) +
                                 ' in row number is ' + str(
                            row)}]


def get_update_create_intake_deadline_application_open_date(intakes, deadlines, application_dates, course, row):
    intakes_deadlines_open_dates_status, intakes_deadlines_open_dates_response = get_intakes_deadline_application_open_dates_list(
        intakes,
        deadlines,
        application_dates,
        row)
    if not intakes_deadlines_open_dates_status:
        return False, intakes_deadlines_open_dates_response

    if len(intakes_deadlines_open_dates_response):
        for intake_deadline_open_date in intakes_deadlines_open_dates_response:
            update_status, update_response = save_course_schedule(intake_deadline_open_date, course, row)
            if not update_status:
                return update_status, update_response
    else:
        return False, [{'key': headers.INTAKE + ' , ' + headers.DEADLINE + ' and ' + headers.APPLICATION_OPEN_DATE,
                        'error': '' + intakes + ' , ' + deadlines + ' and ' + application_dates + ' must be in proper format  and row number is ' + str(
                            row)}]
    return True, None


# date conversion
def get_date(date):
    days = None
    month = None
    year = None
    date = date.strip()
    if len(date.split('-')) == 1:
        month = date
    elif len(date.split('-')) == 2:
        first_part, second_part = date.split('-')
        if len(first_part) == 2 or len(first_part) == 1:
            days = first_part
            month = second_part
        else:
            month = first_part
            year = second_part
    elif len(date.split('-')) == 3:
        days, month, year = date.split('-')

    else:
        return False, ' date is invalid format'
    return parse_date(days, month, year)


def parse_date(days, month, year):
    date_dict = {}
    if days:
        print(get_days(days))
        days_status, days_response = get_days(days)
        if not days_status:
            return days_status, days_response
        date_dict['days'] = days_response
    if month:
        month_status, month_response = get_month(month)
        if not month_status:
            return month_status, month_response
        date_dict['month'] = month_response
    if year:
        year_status, year_response = get_year(year)
        if not year_status:
            return year_status, year_response
        date_dict['year'] = year_response
    return True, date_dict


def get_days(days):
    try:
        days = int(days)
        if 1 <= days <= 31:
            return True, days
        return False, days
    except ValueError:
        return False, 'invalid days its must be integer'



def get_month(month_name):
    if isinstance(month_name, str):
        month_number = None
        month_name = month_name.strip()
        month_name = month_name.lower()
        try:
            if len(month_name) == 3:
                datetime_object = datetime.strptime(month_name, "%b")
                month_number = str(datetime_object.month)
            if len(month_name) > 3:
                datetime_object = datetime.strptime(month_name, "%B")
                month_number = str(datetime_object.month)

            if month_number:
                datetime_object = datetime.strptime(month_number, "%m")
                month_name = datetime_object.strftime("%B")
                return True, month_name
            return False, str(month_name)
        except ValueError:
            return False, str(month_name) + ' invalid month name'


def get_year(year):
    if len(year) == 4:
        return True, year
    if len(year) == 2:
        return True, '20' + year

    return False, None
