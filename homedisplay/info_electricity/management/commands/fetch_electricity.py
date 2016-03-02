import helen_electricity_usage

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from info_electricity.models import Electricity, Note

import datetime


class Command(BaseCommand):
    args = ''
    help = 'Fetches electricity usage information'

    def handle(self, *args, **options):
        helen = helen_electricity_usage.Helen(
            settings.HELEN_USERNAME, settings.HELEN_PASSWORD, settings.HELEN_ID, settings.HELEN_CUSTOMER_ID)
        logged_in = False

        start_date = datetime.datetime.now() - datetime.timedelta(days=93)
        current_date = start_date
        while current_date < datetime.datetime.now() - datetime.timedelta(days=1):  # Current day is never available
            data = Electricity.objects.filter(date=current_date)
            empty_hours = False
            for entry in data:
                if entry.usage == 0:
                    empty_hours = True
            if empty_hours or len(data) != 24:
                # fetch current data.
                if not logged_in:
                    helen.login()
                    logged_in = True
                day_info = helen.get_date(current_date.strftime("%Y%m%d"))
                for entry in day_info:
                    print entry
                    a = datetime.date(entry["year"], entry[
                                      "month"], entry["day"])
                    db_entry, _ = Electricity.objects.get_or_create(
                        date=a, hour=entry["hour"], defaults={"usage": entry["value"]})
                    db_entry.usage = entry["value"]
                    db_entry.save()
                    Note.objects.filter(hour=db_entry).delete()
                    for note in entry["milestones"]:
                        note_entry = Note(hour=db_entry, note=note["note"])
                        note_entry.save()

            current_date += datetime.timedelta(days=1)
