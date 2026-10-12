"""Hypothetical presentation assumptions, not measured business outcomes."""
import json
from pathlib import Path

cases_month = 1000
hourly_value = 600
implementation = 750000
annual_operations = 450000
cost = implementation + annual_operations
scenarios = []
for minutes in (10, 20, 30):
    hours = cases_month * 12 * minutes / 60
    gross = hours * hourly_value
    scenarios.append(dict(minutes=minutes, hours=hours, gross=gross,
                          net=gross-cost, roi=(gross-cost)/cost))
out = dict(cases_month=cases_month, hourly_value=hourly_value,
           implementation=implementation, annual_operations=annual_operations,
           cost=cost, break_even_minutes=cost/(cases_month*12*hourly_value)*60,
           scenarios=scenarios)
Path('tmp/deck/roi.json').write_text(json.dumps(out, indent=2))
