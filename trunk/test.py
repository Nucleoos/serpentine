import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime


def run_test():
    get_nearby()


def get_nearby():
    from gps.models import Trace, Trace_point
    from gps import lib

    tps = Trace_point.objects.get('trace=1')
    t1 = tps[0]
    print t1
    for t in tps:
        if t.trace != t1.trace:
            dist = lib.getDistance(t1.latitude, t1.longitude, t.latitude, t.longitude)
            if dist > 1:
                print u'match' + unicode(t)


start = datetime.now()
print start
run_test()
end = datetime.now()
print end
print 'total time spent: ' + str(end - start)
