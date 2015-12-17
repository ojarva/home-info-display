# coding=utf-8
from django.conf import settings
from django.db import models
from django.utils import timezone
from hsl_api import HSLApi
import datetime

hsl = HSLApi(settings.HSL_USERNAME, settings.HSL_PASSWORD)

__all__ = ["get_departures", "Stop", "LineShow", "Line", "Data"]

def get_departures():
    """ Returns currently active departures per stop. """
    lines = {}
    now = timezone.now()
    for line in Line.objects.select_related("stop__time_needed").filter(show_line=True):
        lines[line.line_number] = {"visible": False, "line": line.line_number, "minimum_time": line.stop.time_needed, "icon": line.icon, "type": line.type, "departures": []}
    for item in Data.objects.filter(line__show_line=True, time__gte=now).order_by("time").prefetch_related("line"):
        if item.line.stop.time_needed < (item.time - now).total_seconds():
            # Only show departures with enough time left
            # Check line schedules
            num = item.line.line_number
            show_line = False
            schedules = False
            for schedule in item.line.show_times.all():
                schedules = True
                if schedule.is_valid():
                    show_line = True
                    break
            if schedules is True and show_line is False:
                continue
            if show_line or schedules is False:
                lines[num]["visible"] = True
            formatted = item.time.isoformat()
            if formatted not in lines[num]["departures"]:
                # Deduplicate departures - this removes duplicate timestamps for busy combined lines
                lines[num]["departures"].append(formatted)
    items = []
    for line in lines:
        if lines[line]["visible"]:
            items.append(lines[line])
    return sorted(items, key=lambda a: a["line"])

class Stop(models.Model):
    description = models.CharField(max_length=50, verbose_name="Kuvaus")
    stop_number = models.CharField(max_length=20, unique=True, verbose_name="Numero")
    time_needed = models.IntegerField(verbose_name="Aika pysäkille", help_text="Kävelyaika kotoa pysäkille (sekunteina)")

    def save(self, *args, **kwargs):
        # fetch lines for this stop
        super(Stop, self).save(*args, **kwargs)
        for line_raw in hsl.get_lines(self.stop_number):
            obj, _ = Line.objects.get_or_create(raw=line_raw, stop=self, defaults={"line_number": hsl.parse_line_number(line_raw), "line_number_raw": hsl.parse_line_number_raw(line_raw), "destination": hsl.parse_destination(line_raw)})
            obj.save()


    def __unicode__(self):
        return u"%s - %s" % (self.stop_number, self.description)

    class Meta:
        verbose_name = "Pysäkki"
        verbose_name_plural = "Pysäkit"

class LineShow(models.Model):
    description = models.CharField(max_length=30, verbose_name="Nimi")
    show_start = models.TimeField(blank=True, null=True, verbose_name="Aloitusaika", help_text="Näytä lähdöt tämän ajan jälkeen")
    show_end = models.TimeField(blank=True, null=True, verbose_name="Lopetusaika", help_text="Näytä lähdöt ennen tätä aikaa")
    show_days = models.CharField(max_length=7, default="1111111", verbose_name="Näytä tiettyinä päivinä", help_text="ma-su, 1=päällä, 0=pois päältä")

    class Meta:
        verbose_name = "Näytön aikataulu"
        verbose_name_plural = "Näytön aikataulut"

    def __unicode__(self):
        return self.description

    def is_valid(self):
        now = datetime.datetime.now()
        current_day = now.weekday()
        if self.show_days[current_day] != "1":
            # Not active on this weekday
            return False
        if self.show_end is not None and self.show_start is not None:
            if self.show_end < self.show_start:
                # Over midnight
                if now.time() > self.show_start:
                    return True
                if now.time() < self.show_end:
                    return True
                return False
        if self.show_start is not None:
            # Start time is set.
            if now.time() < self.show_start:
                # Start time is not yet reached. No need for further checks.
                return False
        if self.show_end is not None:
            if now.time() > self.show_end:
                # Past end time.
                return False
        # No schedule set / schedule matches.
        return True

class Line(models.Model):
    ICONS = (
        ("bus", "bus"),
        ("train", "train"),
        ("subway", "subway"),
        ("ship", "ship"),
        ("plane", "plane"),
    )

    TYPES = (
        ("bus", "bus"),
        ("tram", "tram"),
        ("train", "train"),
        ("metro", "metro"),
        ("ship", "ship"),
        ("plane", "plane"),
    )
    stop = models.ForeignKey("Stop")
    line_number = models.CharField(max_length=20, verbose_name="Numero") # Line number in human readable format.
    line_number_raw = models.CharField(max_length=20) # Line number information in raw format
    raw = models.CharField(max_length=50, verbose_name="Sisäinen numero") # This is internal identification for line. Contains whatever returned by HSL API.
    destination = models.CharField(max_length=50) # Destination for the line

    show_times = models.ManyToManyField("LineShow", blank=True)

    show_line = models.BooleanField(blank=True, default=False, verbose_name="Näytä lähdöt")
    icon = models.CharField(max_length=10, choices=ICONS, verbose_name="Ikoni", default="bus")
    type = models.CharField(max_length=10, choices=TYPES, verbose_name="Tyyppi", help_text="Liikennevälinetyyppi", default="bus")

    def is_valid(self):
        if not self.show_line:
            return False
        for schedule in self.show_times.all():
            if schedule.is_valid():
                return True
        if self.show_times.all().count() == 0:
            # No schedules available - show at all times
            return True
        return False

    class Meta:
        unique_together = ("stop", "raw")
        verbose_name = "Linja"
        verbose_name_plural = "Linjat"

    def __unicode__(self):
        return u"%s - %s (visible: %s)" % (self.stop, self.line_number, self.show_line)

class Data(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    line = models.ForeignKey("Line")
    time = models.DateTimeField()

    class Meta:
        unique_together = ("line", "time")

    def __unicode__(self):
        return u"%s - %s" % (self.line, self.time)
