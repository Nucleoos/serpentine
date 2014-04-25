import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime


def run_test():
    get_matching_segments()



def get_matching_segments():
    from gps.models import Trace, Trace_point

    def get_matching_point(t1):
        matches = {}
        tps = Trace_point.objects.exclude(trace=2)
        tps= tps.extra(where=['20000*(abs('+str(t1.latitude)+'-latitude)+abs('+str(t1.longitude)+'-longitude)) < 1'])
        tps = tps.order_by('order_num')
        if tps.count()>0:
            matches[t1] = tps[0]
        return matches

    alltps = Trace_point.objects.all()
    t1 = alltps.filter(trace=2)[1]
    matches = get_matching_point(t1)
    print matches

    t1 = alltps.filter(trace=2)[10]
    matches = get_matching_point(t1)
    print matches

    t1 = alltps.filter(trace=2)[30]
    matches = get_matching_point(t1)
    print matches

start = datetime.now()
print start
run_test()
end = datetime.now()
print end
print 'total time spent: ' + str(end - start)
