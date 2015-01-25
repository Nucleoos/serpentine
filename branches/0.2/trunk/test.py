# coding: utf-8
import os, datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime
from gps.models import Trace, Trace_property, Trace_point, User
from gps import views
from gps import lib


def run():
    start = datetime.now()
    print(start)
    # run_nearby()
    #run_matching_segments()

    #run_compute_speeds()
    # run_best_performance()
    # run_import_file()
    # run_set_properties()
    #run_tracetabs()
    #run_best_performance()
    run_laps()
    end = datetime.now()
    print(end)
    print('total time spent: ' + str(end - start))

def run_set_properties():
    trs = Trace.objects.all().order_by('-id')
    for tr in trs:
        print tr
        tr.clear_properties()
        tr.set_properties()
        print tr.get_properties()

def run_tracetabs():
    views.trace_tabs_html(None,'/2','/2/332/445')

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
    tr = Trace.objects.get(id=1)
    ppts = Trace_property.objects.filter(trace = tr)

    print tr.get_stats()
    """"print dict
    for vale in dict:
        result = vale[1]
        if result:
            print vale[0]
            print 'result = ', result
            print 'speed ', 3600*result['dist']/result['seconds']
            print 'tps ', result['seconds']/60 , '\'', result['seconds']- 60*(result['seconds']/60), '\'\''
            seckm = int(result['seconds']/result['dist'])
            print 'allure ', seckm/60, seckm-60*(seckm/60)
    """


def run_laps():
    tr = Trace.objects.get(id=12)
    ppts = Trace_property.objects.filter(trace = tr)

    print tr.get_laps()

def run_import_file():
    tr = Trace()
    tr.user = User.objects.get(id=1)
    tr.name = 'test_import'
    tr.ctime = datetime.now()
    tr.save()
    tr.create_from_file('c:/benoit/django/serpentine/media/' + 'import.gpx')

run()