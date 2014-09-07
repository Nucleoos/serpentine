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
    #run_matching_segments()

    #run_compute_speeds()
    run_best_performance()
    end = datetime.now()
    print(end)
    print('total time spent: ' + str(end - start))

def run_compute_speeds():
    trs = Trace.objects.all()
    for tr in trs:
        print tr
        tr.compute_distances()
        tr.compute_speeds()


def run_nearby():
    tr = Trace.objects.get(id=1)
    Trace.get_closest_tracks(tr, 40,0)


def run_matching_segments():
    tr1, tr2 = 11,12
    # tr1 , tr2 = 15,16 # BRM
    tr = Trace.objects.get(id=tr1)
    segments = tr.get_matching_segments_json(tr2)
    print [(segment[0],segment[-1]) for segment in segments]

def run_best_performance():
    tr = Trace.objects.get(id=27)
    print tr
    result = tr.getBestPerformance(10)
    if result:
        print 'result = ', result
        print 'speed ', 3600*result['dist']/result['seconds']
        print 'tps ', result['seconds']/60 , '\'', result['seconds']- 60*(result['seconds']/60), '\'\''
        seckm = int(result['seconds']/result['dist'])
        print 'allure ', seckm/60, seckm-60*(seckm/60)
    else: print result

run()