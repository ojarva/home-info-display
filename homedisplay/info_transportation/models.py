# coding=utf-8
from django.conf import settings
from django.db import models
from django.utils import timezone
from hsl_api import HSLApi

hsl = HSLApi(settings.HSL_USERNAME, settings.HSL_PASSWORD)

def get_departures():
    lines = {}
    now = timezone.now()
    for line in Line.objects.select_related("stop__time_needed").filter(show_line=True):
        lines[line.line_number] = {"line": line.line_number, "minimum_time": line.stop.time_needed, "icon": line.icon, "departures": []}
    for item in Data.objects.select_related("line__line_number", "line__stop__time_needed").filter(line__show_line=True, time__gte=now).order_by("time"):
        if item.line.stop.time_needed < (item.time - now).total_seconds():
            # Only show departures with enough time left
            num = item.line.line_number
            lines[num]["departures"].append(item.time.isoformat())
    items = []
    for line in lines:
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
    description = models.CharField(max_length=30)
    show_start = models.TimeField(blank=True, null=True, verbose_name="Aloitusaika", help_text="Näytä lähdöt tämän ajan jälkeen")
    show_end = models.TimeField(blank=True, null=True, verbose_name="Lopetusaika", help_text="Näytä lähdöt ennen tätä aikaa")
    show_days = models.CharField(max_length=7, default="1111111", verbose_name="Näytä tiettyinä päivinä", help_text="ma-su, 1=päällä, 0=pois päältä")

    def __unicode__(self):
        return self.description

class Line(models.Model):
    ICONS = (
        ("bus", "bus"),
        ("train", "train"),
    )
    stop = models.ForeignKey("Stop")
    line_number = models.CharField(max_length=20, verbose_name="Numero") # Line number in human readable format.
    line_number_raw = models.CharField(max_length=20) # Line number information in raw format
    raw = models.CharField(max_length=50, verbose_name="Sisäinen numero") # This is internal identification for line. Contains whatever returned by HSL API.
    destination = models.CharField(max_length=50) # Destination for the line

    show_times = models.ManyToManyField("LineShow", null=True, blank=True)

    show_line = models.BooleanField(blank=True, default=False, verbose_name="Näytä lähdöt")
    icon = models.CharField(max_length=10, choices=ICONS, verbose_name="Ikoni", default="bus")

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
