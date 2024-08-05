import django
import os
import csv
import re
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from tracker.models.event import Runner

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

def create_runner_list(filename, runner_list):
    csv_columns = read_csv(filename)
    for runner_field in csv_columns['runners']:
        for runner in [re.sub(r'\s*\([^)]*\)', '', m) for m in runner_field.split(", ")]:
            if runner and runner not in runner_list:
                runner_list.append(runner)
                new_runner = Runner(
                    name=runner
                    )
                new_runner.save()

current_runner_list = [instance.name for instance in Runner.objects.all()]
filename = '/home/gsps/tracker/donations/tracker/schedule.csv'
create_runner_list(filename, current_runner_list)
print("Job done!")