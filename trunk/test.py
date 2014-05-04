# coding: utf-8
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime
from gps.models import Trace, Trace_point
from gps import lib

def run():
    start = datetime.now()
    print(start)
    # run_nearby()
    run_matching_segments()
    end = datetime.now()
    print(end)
    print('total time spent: ' + str(end - start))


def run_nearby():
    tr = Trace.objects.get(id=1)
    Trace.get_closest_tracks(tr, 40,0)


def run_matching_segments():
    tr1, tr2 = 11,12
    # tr1 , tr2 = 15,16 # BRM
    tr = Trace.objects.get(id=tr1)
    segments = tr.get_matching_segments_json(tr2)
    print [(segment[0],segment[-1]) for segment in segments]

run()