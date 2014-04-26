import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime


def run_test():
    get_matching_segments()



def get_matching_segments():
    from gps.models import Trace, Trace_point

    def get_matching_point(t1,tr_id, tr2_id, min_order_num):
        matches = {}
        tps = Trace_point.objects.exclude(trace=tr_id)
        tps = tps.filter(order_num__gt = min_order_num).filter(trace=tr2_id)
        tps= tps.extra(where=['20000*(abs('+str(t1.latitude)+'-latitude)+abs('+str(t1.longitude)+'-longitude)) < 1'])
        tps = tps.order_by('order_num')
        # print tps.query
        if tps.count()>0:
            matches[t1] = tps[0]
        return matches

    alltps = Trace_point.objects.all()
    min_num = 0
    tps = alltps.filter(trace=2)
    for t1 in tps:
        matches = get_matching_point(t1,2,3,min_num)
        if matches!={}:
            min_num = matches.values()[0].order_num
            print 'num' + str(min_num) + ' ' + str(matches)

start = datetime.now()
print start
run_test()
end = datetime.now()
print end
print 'total time spent: ' + str(end - start)
