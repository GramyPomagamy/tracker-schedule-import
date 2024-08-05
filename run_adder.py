import django
import os
import csv
import re
import sys
import inspect
import datetime

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from tracker.models.event import Event, Runner, SpeedRun

def read_csv(filename):
    csv_columns = {}
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        col_headers = next(reader)
        for header in col_headers:
            csv_columns[header] = []
        for row in reader:
            for i, value in enumerate(row):
                csv_columns[col_headers[i]].append(value)
    return csv_columns

def create_runs(filename):
    csv_columns = read_csv(filename)
    starting_day = datetime.datetime.strptime(csv_columns['time'][0][:10], '%Y-%m-%d')
    event = Event.objects.filter(datetime__gt=starting_day, datetime__lt=starting_day+datetime.timedelta(days=1)).get()
    sleep_breaks_modifier = 0
    for i in range(len(csv_columns['time'])):
        if not csv_columns['game'][i]:
            previous_run = SpeedRun.objects.filter(**{'event': event, 'order': i-sleep_breaks_modifier}).get()
            hours, minutes, seconds = map(int, previous_run.setup_time.split(':'))
            hours2, minutes2, seconds2 = map(int, csv_columns['setup_time'][i].split(':'))
            total_time = (hours+hours2)*3600 + (minutes+minutes2)*60 + (seconds+seconds2)
            sleeping_setup = f'{(total_time//3600):02}:{((total_time%3600)//60):02}:{(total_time%60):02}'
            previous_run.setup_time = sleeping_setup
            previous_run.save()
            sleep_breaks_modifier += 1
            continue
        category = csv_columns['category'][i]
        console = csv_columns['console'][i]
        order = i+1-sleep_breaks_modifier
        run_time = csv_columns['estimate'][i]
        setup_time = csv_columns['setup_time'][i]
        coop = any(p in csv_columns['type'][i] for p in ["Coop", "Relay"])
        runners = [re.sub(r'\s*\([^)]*\)', '', m) for m in csv_columns['runners'][i].split(", ")]
        if "(Bonus -" in csv_columns['game'][i]:
            name = " ".join(csv_columns['game'][i].split(" ")[:-4])+" (Bonus)"
        else:
            name = csv_columns['game'][i] 
        new_run = SpeedRun(
            category=category,
            console=console,
            event=event,
            order=order,
            run_time=run_time,
            setup_time=setup_time,
            coop=coop,
            name=name,
            display_name=name,
            deprecated_runners=", ".join(runners)
            )
        new_run.save()
        if runners[0]:
            for person in runners:
                new_run.runners.add(Runner.objects.filter(**{'name': person}).get())
            new_run.save()

filename = '/home/gsps/tracker/donations/tracker/schedule.csv'
create_runs(filename)
print("Job done!")