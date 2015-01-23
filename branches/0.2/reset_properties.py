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
    run_reset_properties()
    run_reset_order_nums()
    end = datetime.now()
    print(end)
    print('total time spent: ' + str(end - start))

def run_reset_properties():
    trs = Trace.objects.all().order_by('-id')
    for tr in trs:
        print tr
        if tr.id < 106:
            tr.clear_properties()
            tr.set_properties()
            print tr.get_properties()


from django.db import transaction

@transaction.commit_manually
def run_reset_order_nums():
    trs = Trace.objects.all().order_by('-id')
    for tr in trs:
        if tr.id < 106:
            print tr
            tps = Trace_point.objects.filter(trace=tr).order_by('time')
            i=0
            for tp in tps:
                i+=1
                tp.order_num=i
                tp.save()
            transaction.commit()
run()