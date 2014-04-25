import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime


def run_test():
    get_matching_segments()


def get_matching_segments():
    from gps.models import Trace, Trace_point
    from gps import lib

    alltps = Trace_point.objects.all()
    t1 = alltps.filter(trace=2)[0]
    print t1
    tps = Trace_point.objects.exclude(trace=2)
    tps= tps.extra(where=['20000*(abs('+str(t1.latitude)+'-latitude)+abs('+str(t1.longitude)+'-longitude)) < 1'])
    tps = tps.order_by('order_num')
    # if tps.count()>0:
    print tps[0]

start = datetime.now()
print start
run_test()
end = datetime.now()
print end
print 'total time spent: ' + str(end - start)
