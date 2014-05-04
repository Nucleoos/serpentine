# coding: utf-8
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime
from gps.models import Trace, Trace_point
from gps import lib

def run_test():
    tr1, tr2 = 11,12
    # tr1 , tr2 = 15,16 # BRM
    tr = Trace.objects.get(id=tr1)
    segments = tr.get_matching_segments(tr2)
    print [(segment[0],segment[-1]) for segment in segments]


start = datetime.now()
print(start)
run_test()
end = datetime.now()
print(end)
print('total time spent: ' + str(end - start))

