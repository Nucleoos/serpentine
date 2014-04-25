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
    match = 0
    dist = 0
    for t in tps:
        # dist = 1000*lib.getDistance(t1.latitude, t1.longitude, t.latitude, t.longitude)
        diff = 20000* (abs(t1.latitude-t.latitude) + abs(t1.longitude - t.longitude))
        if diff < 1:
            print u'match '+ unicode(dist)+ ' diff '+ unicode(diff) + '  ' + unicode(t)
            match += 1
    print 'matches ' + str(match)


start = datetime.now()
print start
run_test()
end = datetime.now()
print end
print 'total time spent: ' + str(end - start)
