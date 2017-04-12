from __future__ import unicode_literals

from django.db import models


class Tail(models.Model):
    number = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.number


class Line(models.Model):
    name = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def flights(self):
        line_parts = self.linepart_set.all().values('number')
        flight_numbers = [lp['number'] for lp in line_parts]
        return Flight.objects.filter(number__in=flight_numbers)


class LinePart(models.Model):
    number = models.CharField(default='', max_length=10, null=False, blank=False)

    line = models.ForeignKey(Line, null=True, blank=False)

    def __unicode__(self):
        return self.number


class Flight(models.Model):
    number = models.CharField(db_index=True, max_length=10, default=0, null=False, blank=False)
    origin = models.CharField(max_length=10, blank=False)
    destination = models.CharField(max_length=10, blank=False)
    departure_datetime = models.DateTimeField(null=False, blank=False)
    arrival_datetime = models.DateTimeField(null=False, blank=False)

    # line = models.ForeignKey(Line, null=True, blank=False)

    def __unicode__(self):
        return str(self.number) + '. ' + self.origin + '-' + self.destination

    @property
    def length(self):
        return (self.arrival_datetime - self.departure_datetime).total_seconds()


class Assignment(models.Model):
    STATUS_CHOICES = (
        (1, 'Flight'),
        (2, 'Maintenance'),
        (3, 'Unscheduled Flight'),
    )

    flight_number = models.CharField(max_length=10, default='', null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=False, blank=False)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    flight = models.ForeignKey(Flight, null=True, blank=False)
    tail = models.ForeignKey(Tail, null=True, blank=False)

    def __unicode__(self):
        if self.status == 1:
            return 'Flight ' + str(self.flight_number) + ' Assignment'
        elif self.status == 2:
            return 'Maintenance'
        elif self.status == 3:
            return 'Unscheduled Flight'
        else:
            return 'Other'

    @classmethod
    def is_duplicated(cls, tail, start_time, end_time, exclude_check_assignment=None):
        # start time check

        query = cls.objects.filter(
            tail=tail,
            start_time__lte=start_time,
            end_time__gt=start_time
        )
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        dup_count = query.count()
        if dup_count > 0:
            return True

        # end time check

        query = cls.objects.filter(
            tail=tail,
            start_time__lt=end_time,
            end_time__gte=end_time
        )
        if exclude_check_assignment:
            query = query.exclude(pk=exclude_check_assignment.id)
        dup_count = query.count()
        if dup_count > 0:
            return True

        return False
