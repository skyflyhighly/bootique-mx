from datetime import timedelta, datetime
import json
import dateutil.parser
import random
import os
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.middleware import csrf
from django.db.models import Q, ProtectedError, Max
from django.conf import settings

from routeplanning.models import *
from routeplanning.forms import *
from common.helpers import *
from common.decorators import *


@login_required
@gantt_readable_required
def index(request):
    mode = request.GET.get('mode') if request.GET.get('mode') else '1'
    start_tmstmp = request.GET.get('start')

    tails = Tail.objects.all()
    lines = Line.objects.order_by('name').all()

    days_options = { '1': 1, '2': 1, '3': 1, '4': 1, '5': 3, '6': 7, }          # Date mark count
    hours_options = { '1': 3, '2': 6, '3': 12, '4': 24, '5': 24, '6': 6, }      # Hours mark count
    units_per_hour_options = { '1': 4, '2': 2, '3': 1, '4': 1, '5': 1, '6': 0.25, }

    if request.GET.get('days'):
        days = int(request.GET.get('days'))
        days = 14 if days > 14 else days
        days = 1 if days < 1 else days
        if days > 3:
            mode = '6'
    else:
        days = days_options[mode]

    hours = hours_options[mode]
    units_per_hour = units_per_hour_options[mode]

    if not start_tmstmp:
        start_time = datetime_now_utc()
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_tmstmp = totimestamp(start_time)

    big_unit_colspan = units_per_hour * hours if units_per_hour > 1 else hours
    big_unit_count = 14 * (24 / hours) if days == 1 else 14
    big_units = range(0, big_unit_count)
    small_units = range(0, big_unit_colspan * big_unit_count)
    table_length_in_secs = 14 * 24 * 3600

    context = {
        'tails': tails,
        'lines': lines,
        'big_units': big_units,
        'small_units': small_units,
        'days': days,
        'hours': hours,
        'big_unit_colspan': big_unit_colspan,
        'units_per_hour': units_per_hour,
        'mode': mode,
        'start_tmstmp': start_tmstmp,
        'prev_start_tmstmp': int(start_tmstmp) - table_length_in_secs,
        'next_start_tmstmp': int(start_tmstmp) + table_length_in_secs,
        'csrf_token': csrf.get_token(request),
        'window_at_end': request.GET.get('window_at_end') or 0,
    }
    return render(request, 'gantt.html', context)

@login_required
@gantt_writable_required
def add_tail(request):
    form = TailForm(request.POST or None)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if form.is_valid():
            tail = form.save()

            if action_after_save == 'save-and-continue':
                return redirect('routeplanning:edit_tail', tail_id=tail.id)
            elif action_after_save == 'save':
                return redirect('routeplanning:index')
            elif action_after_save == 'save-and-add-another':
                form = TailForm()

    tails = Tail.objects.all()
    context = {
        'form': form,
        'title': 'Add Tail',
        'tails': tails,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'tail.html', context)

@login_required
@gantt_readable_required
def edit_tail(request, tail_id=None):
    tail = get_object_or_404(Tail, pk=tail_id)

    form = TailForm(request.POST or None, instance=tail)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if not can_write_gantt(request.user):
            return HttpResponseForbidden()
        if form.is_valid():
            tail = form.save()

            if action_after_save == 'save-and-add-another':
                return redirect('routeplanning:add_tail')
            elif action_after_save == 'save':
                return redirect('routeplanning:index')
            elif action_after_save == 'save-and-add-another':
                form = LineForm()

    tails = Tail.objects.all()
    context = {
        'form': form,
        'title': 'Edit Tail ' + tail.number,
        'tails': tails,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'tail.html', context)

@login_required
@gantt_writable_required
def delete_tail(request, tail_id=None):
    result = {
        'success': False,
    }
    if request.method == 'DELETE':
        try:
            if tail_id:
                tail = Tail.objects.get(pk=tail_id)
                tail.delete()
                result['success'] = True
            else:
                result['error'] = 'Tail id should be specified'
        except:
            result['error'] = 'Error occurred while deleting tail'
    else:
        result['error'] = 'Only DELETE method allowed for this api'
    return JsonResponse(result, safe=False)

@login_required
@gantt_writable_required
def add_line(request):
    form = LineForm(request.POST or None)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if form.is_valid():
            line = Line(name=form.cleaned_data['name'])    
            line.save()

            for i in range(1, 12):
                entered_line_part_number = form.cleaned_data['part' + str(i)]
                if entered_line_part_number:
                    line_part = LinePart(number=entered_line_part_number, line=line)    
                    line_part.save()
                else:
                    break

            if action_after_save == 'save-and-continue':
                return redirect('routeplanning:edit_line', line_id=line.id)
            elif action_after_save == 'save-and-add-another':
                form = LineForm()
            elif action_after_save == 'save':
                return redirect('routeplanning:index')

    lines = Line.objects.all()
    context = {
        'form': form,
        'title': 'Add Line',
        'lines': lines,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'line.html', context)

@login_required
@gantt_readable_required
def edit_line(request, line_id=None):
    line = get_object_or_404(Line, pk=line_id)

    initialData = {
        'name': line.name,
    }
    for i, line_part in enumerate(line.linepart_set.all()):
        initialData['part' + str(i)] = line_part.number

    form = LineForm(request.POST or initialData)
    action_after_save = request.POST.get('action_after_save')

    if request.method == 'POST':
        if not can_write_gantt(request.user):
            return HttpResponseForbidden()
        if form.is_valid():
            if line.name != form.cleaned_data['name']:
                line.name = form.cleaned_data['name']
                line.save()

            for i in range(1, 12):
                entered_line_part_number = form.cleaned_data['part' + str(i)]
                if entered_line_part_number:
                    try:
                        line_part = line.linepart_set.get(number=i)
                        if line_part.number != entered_line_part_number:
                            line_part.number = entered_line_part_number
                            line_part.save()
                    except:
                        line_part = LinePart(number=entered_line_part_number, line=line)    
                        line_part.save()
                else:
                    break

            if action_after_save == 'save-and-add-another':
                return redirect('routeplanning:add_line')
            elif action_after_save == 'save':
                return redirect('routeplanning:index')
            elif action_after_save == 'save-and-add-another':
                form = LineForm()

    lines = Line.objects.all()
    context = {
        'form': form,
        'title': 'Edit Line ' + line.name,
        'lines': lines,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'line.html', context)

@login_required
@gantt_writable_required
def delete_line(request, line_id=None):
    result = {
        'success': False,
    }
    if request.method == 'DELETE':
        try:
            if line_id:
                line = Line.objects.get(pk=line_id)
                line.delete()
                result['success'] = True
            else:
                result['error'] = 'Line id should be specified'
        except:
            result['error'] = 'Error occurred while deleting line'
    else:
        result['error'] = 'Only DELETE method allowed for this api'
    return JsonResponse(result, safe=False)

@login_required
@gantt_writable_required
def flights(request):
    flights = Flight.objects.all()

    context = {
        'flights': flights,
        'csrf_token': csrf.get_token(request),
    }
    return render(request, 'flights.html', context)

@login_required
@gantt_writable_required
def add_flight(request):
    form = FlightForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            flight = form.save()
            return redirect('routeplanning:edit_flight', flight_id=flight.id)

    context = {
        'form': form,
        'title': 'Add Flight',
    }
    return render(request, 'flight.html', context)

@login_required
@gantt_writable_required
def edit_flight(request, flight_id=None):
    flight = get_object_or_404(Flight, pk=flight_id)
    form = FlightForm(request.POST or None, instance=flight)
    if request.method == 'POST':
        if form.is_valid():
            form.save()

    context = {
        'form': form,
        'title': 'Edit Flight',
    }
    return render(request, 'flight.html', context)

@login_required
@gantt_writable_required
def delete_flights(request):
    if request.method == 'POST':
        ids_string = request.POST.get('flight_ids')
        ids = ids_string.split(',')
        for id in ids:
            try:
                Flight.objects.filter(pk=id).delete()
            except ProtectedError:
                pass
    return redirect('routeplanning:flights')

@login_required
@gantt_readable_required
def api_load_data(request):
    start_time = datetime.fromtimestamp(int(request.GET.get('startdate')), tz=utc)
    end_time = datetime.fromtimestamp(int(request.GET.get('enddate')), tz=utc)

    template_data = []
    lines = Line.objects.all()
    for line in lines:
        flights = line.flights.filter(
            (Q(departure_datetime__gte=start_time) & Q(departure_datetime__lte=end_time)) |
            (Q(arrival_datetime__gte=start_time) & Q(arrival_datetime__lte=end_time)) |
            (Q(departure_datetime__lte=start_time) & Q(arrival_datetime__gte=end_time))
        )
        for flight in flights:
            flight_data = {
                'id': flight.id,
                'number': flight.number,
                'origin': flight.origin,
                'destination': flight.destination,
                'departure_datetime': flight.departure_datetime,
                'arrival_datetime': flight.arrival_datetime,
                'line_id': line.id,
            }
            template_data.append(flight_data)

    assignments_data = []
    assignments = Assignment.objects.select_related('flight', 'tail').filter(
        (Q(start_time__gte=start_time) & Q(start_time__lte=end_time)) |
        (Q(end_time__gte=start_time) & Q(end_time__lte=end_time)) |
        (Q(start_time__lte=start_time) & Q(end_time__gte=end_time))
    )
    for assignment in assignments:
        assignment_data = {
            'id': assignment.id,
            'number': assignment.flight_number,
            'start_time': assignment.start_time,
            'end_time': assignment.end_time,
            'status': assignment.status,
            'tail': assignment.tail.number,
        }
        if assignment.flight:
            assignment_data['origin'] = assignment.flight.origin
            assignment_data['destination'] = assignment.flight.destination
            assignment_data['departure_datetime'] = assignment.flight.departure_datetime
            assignment_data['arrival_datetime'] = assignment.flight.arrival_datetime
            assignment_data['flight_id'] = assignment.flight.id
        assignments_data.append(assignment_data)

    data = {
        'assignments': assignments_data,
        'templates': template_data,
    }
    return JsonResponse(data, safe=False)

@login_required
@gantt_writable_required
def api_assign_flight(request):
    result = {
        'success': False,
        'assigned_flights': {},
    }

    if request.method != 'POST':
        result['error'] = 'Only POST method is allowed'
        return JsonResponse(result, safe=False)

    try:
        flight_data = json.loads(request.POST.get('flight_data'))
    except:
        result['error'] = 'Invalid parameters'
        return JsonResponse(result, safe=False, status=400)

    for data in flight_data:
        try:
            flight_id = data['flight']
            tail_number = data['tail']
            tail = Tail.objects.get(number=tail_number)
            flight = Flight.objects.get(pk=flight_id)

            if not Assignment.is_duplicated(tail, flight.departure_datetime, flight.arrival_datetime):
                assignment = Assignment(
                    flight_number=flight.number,
                    start_time=flight.departure_datetime,
                    end_time=flight.arrival_datetime,
                    status=1,
                    flight=flight,
                    tail=tail
                )
                assignment.save()
                result['assigned_flights'][flight_id] = assignment.id
        except Exception as e:
            print(str(e))

    result['success'] = True
    return JsonResponse(result, safe=False)

@login_required
@gantt_writable_required
def api_assign_status(request):
    result = {
        'success': False,
    }

    if request.method != 'POST':
        result['error'] = 'Only POST method is allowed'
        return JsonResponse(result, safe=False)

    try:
        tail_number = request.POST.get('tail')
        start_time = dateutil.parser.parse(request.POST.get('start_time'))
        end_time = dateutil.parser.parse(request.POST.get('end_time'))
        status = request.POST.get('status')
    except:
        result['error'] = 'Invalid parameters'
        return JsonResponse(result, safe=False, status=400)

    try:
        tail = Tail.objects.get(number=tail_number)
        if Assignment.is_duplicated(tail, start_time, end_time):
            result['error'] = 'Duplicated assignment'
            return JsonResponse(result, safe=False)

        assignment = Assignment(
            flight_number=0,
            start_time=start_time,
            end_time=end_time,
            status=status,
            flight=None,
            tail=tail
        )
        assignment.save()
    except Exception as e:
        result['error'] = str(e)
        return JsonResponse(result, safe=False, status=500)

    result['success'] = True
    result['id'] = assignment.id
    return JsonResponse(result, safe=False)

@login_required
@gantt_writable_required
def api_remove_assignment(request):
    result = {
        'success': False,
        'removed_assignments': [],
    }

    if request.method != 'POST':
        result['error'] = 'Only POST method is allowed'
        return JsonResponse(result, safe=False)

    try:
        assignment_ids = json.loads(request.POST.get('assignment_data'))
    except:
        result['error'] = 'Invalid parameters'
        return JsonResponse(result, safe=False, status=400)

    for assignment_id in assignment_ids:
        try:
            assignment = Assignment.objects.get(pk=assignment_id)
            assignment.delete()
            result['removed_assignments'].append(assignment_id)
        except Exception as e:
            print(str(e))

    result['success'] = True
    return JsonResponse(result, safe=False)

@login_required
@gantt_writable_required
def api_move_assignment(request):
    result = {
        'success': False,
        'assignments': {},
    }

    if request.method != 'POST':
        result['error'] = 'Only POST method is allowed'
        return JsonResponse(result, safe=False)

    try:
        assignment_data = json.loads(request.POST.get('assignment_data'))
    except:
        result['error'] = 'Invalid parameters'
        return JsonResponse(result, safe=False, status=400)

    for data in assignment_data:
        try:
            assignment_id = data['assignment_id']
            tail_number = data['tail']
            try:
                start_time_str = data['start_time']
                if start_time_str:
                    start_time = dateutil.parser.parse(start_time_str)
                else:
                    start_time = None
            except:
                start_time_str = None
                start_time = None

            assignment = Assignment.objects.get(pk=assignment_id)
            tail = Tail.objects.get(number=tail_number)

            if not start_time:
                start_time = assignment.start_time
                end_time = assignment.end_time
            else:
                end_time = start_time + (assignment.end_time - assignment.start_time)

            if not Assignment.is_duplicated(tail, start_time, end_time, assignment):
                assignment.tail = tail
                if start_time_str:
                    assignment.start_time = start_time
                    assignment.end_time = end_time
                assignment.save()
                result['assignments'][assignment.id] = {
                    'start_time': assignment.start_time.isoformat(),
                    'end_time': assignment.end_time.isoformat(),
                }
        except Exception as e:
            print(str(e))

    result['success'] = True
    return JsonResponse(result, safe=False)

@login_required
@gantt_writable_required
def api_resize_assignment(request):
    result = {
        'success': False,
    }

    if request.method != 'POST':
        result['error'] = 'Only POST method is allowed'
        return JsonResponse(result, safe=False)

    try:
        assignment_id = request.POST.get('assignment_id')
        pos = request.POST.get('position')  # start or end
        diff_seconds = round(float(request.POST.get('diff_seconds')) / 300.0) * 300.0     # changed time in seconds
    except:
        result['error'] = 'Invalid parameters'
        return JsonResponse(result, safe=False, status=400)

    try:
        assignment = Assignment.objects.get(pk=assignment_id)

        start_time = assignment.start_time
        end_time = assignment.end_time
        if pos == 'end':
            end_time = end_time + timedelta(seconds=diff_seconds)
        else:
            start_time = start_time - timedelta(seconds=diff_seconds)

        if start_time >= end_time:
            result['error'] = 'Start time cannot be later than end time'
            return JsonResponse(result, safe=False, status=400)

        if Assignment.is_duplicated(assignment.tail, start_time, end_time, assignment):
            result['error'] = 'Duplicated assignment'
            return JsonResponse(result, safe=False)

        assignment.start_time = start_time
        assignment.end_time = end_time
        assignment.save()
    except Exception as e:
        result['error'] = str(e)
        return JsonResponse(result, safe=False, status=500)

    result['success'] = True
    result['start_time'] = assignment.start_time.isoformat()
    result['end_time'] = assignment.end_time.isoformat()
    return JsonResponse(result, safe=False)

def str_to_datetime(str):
    parts = str.split(' ')
    date_parts = parts[0].split('/')
    date = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])
    hour = 0
    minute = 0
    second = 0

    if len(parts) > 1:
        time_parts = parts[1].split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2])

    return datetime(year, month, date, hour, minute, second, tzinfo=utc)

@login_required
@gantt_writable_required
def api_upload_csv(request):
    result = {
        'success': False,
    }

    filepath = settings.STATIC_ROOT + 'uploads/' + str(totimestamp(datetime_now_utc())) + '_' + str(random.randint(100000, 999999)) + '.csv'
    try:
        file = request.FILES['csvfile']
        destination = open(filepath, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
            destination.close()
    except:
        result['error'] = 'Failed to upload file to server.'
        return JsonResponse(result, safe=False)

    with open(filepath) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        now = datetime_now_utc()
        import pdb; pdb.set_trace()

        for row in csvreader:
            try:
                flight_number = int(row[1][3:])
                origin = row[2]
                destination = row[3]
                departure_datetime = str_to_datetime(row[4])
                arrival_datetime = str_to_datetime(row[6])

                # if departure_datetime < now:
                #     continue

                flight_to_update = None

                closest_past_date = Flight.objects \
                    .filter(number=flight_number, departure_datetime__lte=departure_datetime) \
                    .aggregate(closest_past_date=Max('departure_datetime'))['closest_past_date']

                flight_just_before = Flight.objects.select_related('assignment').get(
                    number=flight_number,
                    departure_datetime=closest_past_date
                )

                if closest_past_date.year == departure_datetime.year \
                    and closest_past_date.month == departure_datetime.month \
                    and closest_past_date.day == departure_datetime.day:

                    flight_to_update = flight_just_before
                else:
                    closest_next_date = Flight.objects \
                        .filter(number=flight_number, departure_datetime__gt=departure_datetime) \
                        .aggregate(closest_next_date=Max('departure_datetime'))['closest_next_date']

                    flight_just_after = Flight.objects.select_related('assignment').get(
                        number=flight_number,
                        departure_datetime=closest_next_date
                    )

                    if closest_next_date.year == departure_datetime.year \
                        and closest_next_date.month == departure_datetime.month \
                        and closest_next_date.day == departure_datetime.day:
                        flight_to_update = flight_just_after

                if flight_to_update:
                    flight_to_update.departure_datetime = departure_datetime
                    flight_to_update.arrival_datetime = arrival_datetime
                    flight_to_update.save()

                    assignment = flight_to_update.get_assignment()
                    if assignment:
                        dup_assignments = Assignment.get_duplicated_assignments(assignment.tail, departure_datetime, arrival_datetime, assignment)
                        if dup_assignments.count() > 0:
                            assignment.delete()
                            dup_assignments.delete()
                        else:
                            assignment.start_time = departure_datetime
                            assignment.end_time = arrival_datetime
                            assignment.save()
                else:
                    flight=Flight(
                        number=flight_number,
                        origin=origin,
                        destination=destination,
                        departure_datetime=departure_datetime,
                        arrival_datetime=arrival_datetime
                    )
                    flight.save()

            except:
                pass

    try:
        os.remove(filepath)
    except:
        pass

    result['success'] = True
    return JsonResponse(result, safe=False)
