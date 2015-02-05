from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from info_birthdays.models import Birthday
from datetime import date

class Command(BaseCommand):
    args = ''
    help = 'Imports <name>[, nickname] <birthday> formatted birthdays from file'

    def handle(self, *args, **options):
        f = open(args[0])
        for line in f:
            line = line.strip()
            line = line.rsplit(" ", 1)
            if len(line) != 2:
                continue
            name = line[0].split(",")
            full_name = name[0].strip()
            if len(name) == 2:
                nickname = name[1].strip()
            else:
                nickname = None
            birthday = line[1]

            exists = Birthday.objects.filter(name=full_name).count()
            if exists > 0:
                print full_name, "already exists. Skipping"
                continue
            birthday = birthday.split(".")
            day = int(birthday[0])
            month = int(birthday[1])
            if len(birthday[2]) == 0:
                year = 1970
                valid_year = False
            else:
                valid_year = True
                year = int(birthday[2])
            birthday = date(year, month, day)
            print full_name, nickname, birthday
            a = Birthday(name=full_name, nickname=nickname, birthday=birthday, valid_year=valid_year)
            a.save()
