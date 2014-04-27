# coding: utf-8
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime


def run_test():
   for i in  get_matching_segments(1,2):
       print i



def get_matching_segments(tr1_id,tr2_id):
    from gps.models import Trace, Trace_point

    def get_matching_points(tp1 ,tr2_id, num_min = 0, exclude_list = []):
        """ renvoie pour tp1 les points de t2 susceptible de matcher les points de t1
            avec un order_num >= à order_min
        """
        match = {}
        tps = Trace_point.objects.filter(trace=tr2_id)
        if num_min != 0:
            tps = tps.filter(order_num__lt = num_min +100)
        if len(exclude_list)>9000:
            print exclude_list
        tps = tps.filter(order_num__gt = num_min).exclude(order_num__in=exclude_list)
        tps = tps.extra(where=['20000*(abs('+str(tp1.latitude)+'-latitude)+abs('+str(tp1.longitude)+'-longitude)) < 3']) #todo approx plane for dist
        tps = tps.order_by('order_num')
        # print tps.query
        if tps.count()>0:
            match[tp1] = tps
        return match

    alltps = Trace_point.objects.all()
    tps = alltps.filter(trace=tr1_id)[::10]
    matches = [] #liste de points matchants
    t1_order_num = 0
    t2_exclude_list = [] #liste des points déjà matchés dans t2=> à exclure
    matching_segments = [] #liste de matches dont la longueur est suffisante
    for t1 in tps:
        if t1.order_num > t1_order_num:
            t1_order_num = t1.order_num
            match = get_matching_points(t1, tr2_id, 0,[x[1] for x in matches]+t2_exclude_list)
            if match != {}:
                matches.append((match.keys()[0].order_num, match.values()[0][0].order_num))
                min_num = match.values()[0][0].order_num
                # try to build a segment
                segtps = alltps.filter(trace=tr1_id).filter(order_num__gt=t1.order_num)
                n_unmatch = 0
                for tp in segtps:
                    t1_order_num = tp.order_num
                    match = get_matching_points(tp,tr2_id,min_num,[x[1] for x in matches]+t2_exclude_list)
                    if match == {}:
                        n_unmatch += 1
                        if n_unmatch > 20:
                            break
                    else:
                        matches.append((match.keys()[0].order_num, match.values()[0][0].order_num))
                        min_num = match.values()[0][0].order_num
                        n_unmatch=0
                if len(matches) > 20: #TODO faire un check de distance
                    matching_segments.append(matches)
                    t2_exclude_list += [x[1] for x in matches]
                matches = []

    return matching_segments

start = datetime.now()
print start
run_test()
end = datetime.now()
print end
print 'total time spent: ' + str(end - start)
