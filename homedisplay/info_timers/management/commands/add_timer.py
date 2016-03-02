from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from info_timers.models import Timer
from optparse import make_option
import datetime


class Command(BaseCommand):
    args = ''
    help = 'Add new timer'

    option_list = BaseCommand.option_list + (
        make_option('--name',
                    action='store',
                    type='string',
                    dest='name',
                    help='Timer name'),
        make_option('--duration',
                    action='store',
                    type='string',
                    default='3600',
                    help='Timer duration (in seconds)'),
        make_option('--no-bell',
                    action='store_true',
                    dest='no_bell',
                    default=False,
                    help='Do not show "alarm until dismissed" button'),
        make_option('--auto-remove',
                    action='store',
                    dest='auto_remove',
                    help='Automatically remove after overdue by N seconds'),
        make_option('--start-time',
                    action='store',
                    dest='start_time',
                    help='Start time (HH:MM)'),
        make_option('--start-date',
                    action='store',
                    dest='start_date',
                    help='Start date (YYYY-MM-DD)')
    )

    def handle(self, *args, **options):
        if not options["name"]:
            raise CommandError("Missing mandatory --name parameter")

        try:
            duration = int(options["duration"])
            assert duration > 0
        except:
            raise CommandError("--duration must be positive integer")

        if options["auto_remove"]:
            try:
                auto_remove = int(options["auto_remove"])
                assert auto_remove > 0
            except:
                raise CommandError("--auto-remove must be positive integer")
        else:
            auto_remove = None

        if options["start_time"]:
            try:
                t = options["start_time"].split(":")
                start_time = datetime.time(int(t[0]), int(t[1]))
            except:
                raise CommandError("--start-time format must be HH:MM")
        else:
            start_time = datetime.datetime.now().time()

        if options["start_date"]:
            try:
                t = options["start_date"].split("-")
                start_date = datetime.date(int(t[0]), int(t[1]), int(t[2]))
            except:
                raise CommandError("--start-date format must be YYYY-MM-DD")
        else:
            start_date = datetime.datetime.now().date()

        start_time = datetime.datetime.combine(start_date, start_time)
        start_time = timezone.make_aware(
            start_time, timezone.get_current_timezone())
        timer = Timer(name=options["name"], no_bell=options[
                      "no_bell"], auto_remove=auto_remove, start_time=start_time, duration=duration)
        timer.save()
