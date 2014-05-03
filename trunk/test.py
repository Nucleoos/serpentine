# coding: utf-8
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime
from gps.models import Trace, Trace_point
from gps import lib

def run_test():
    tr1, tr2 = 7,8
    # tr1 , tr2 = 15,16 # BRM
    tr = Trace.objects.get(id=tr1)
    print tr
    print tr.get_total_time() / Trace_point.objects.filter(trace=tr).count()
    print [Trace_point.objects.filter(trace=tr)[1]]
    #segments .= tr.get_matching_segments(tr2)
    #for segment in segments:
     #   print(segment)

def get_matching_segments(tr1_id,tr2_id,length_tolerance=20):

    #TODO: use excluded ranges instead of excluded lists
    def get_matching_points(tp1 ,tr2_id, num_min = 0, exclude_list = [],length_tolerance = 30):
        """ renvoie pour tp1 les points de t2 susceptible de matcher les points de t1
            avec un order_num >= à order_min
        """
        match = {}
        tps = Trace_point.objects.filter(trace=tr2_id)
        if num_min != 0:
            tps = tps.filter(order_num__lt = num_min +length_tolerance)
        if len(exclude_list)>950:
        #handling sqlite limitations (but exclude list should not be so long) i should use excluded_ranges cf previous to do.
        # this is artificially introducing a maxlength to the matching segment
            return {}
        tps = tps.filter(order_num__gt = num_min).exclude(order_num__in=exclude_list)
        tps = tps.extra(where=['10000*(abs('+str(tp1.latitude)+'-latitude)+abs('+str(tp1.longitude)+'-longitude)) < 2']) #todo approx plane for dist
        # tps = tps.extra(where=['power(3,2)<3'])
        tps = tps.order_by('order_num')
        # print tps.query
        if tps.count()>0:
            min_dist = 1 #on commence avec 1 km
            tp2 = tps[0]
            for t in tps:
                # dist = lib.getDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                dist = lib.getQuickDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                if dist < min_dist:
                    min_dist = dist
                    tp2 = t
            if min_dist < 0.010:
                match[tp1] = tp2
            else:
                return {}
        return match

    alltps = Trace_point.objects.all()
    tps = alltps.filter(trace=tr1_id)[::length_tolerance]
    matches = [] #liste de points matchants
    t1_order_num = 0
    t2_exclude_list = [] #liste des points déjà matchés dans t2=> à exclure
    matching_segments = [] #liste de matches dont la longueur est suffisante
    for t1 in tps:
        if t1.order_num > t1_order_num:
            t1_order_num = t1.order_num
            match = get_matching_points(t1, tr2_id, 0,[x[1] for x in matches]+t2_exclude_list,length_tolerance)
            if match != {}:
                # matches.append((match.keys()[0].order_num, match.values()[0][0].order_num))
                min_num = match.values()[0].order_num
                # try to build a segment
                segtps = alltps.filter(trace=tr1_id).filter(order_num__gt=t1.order_num-length_tolerance)
                n_unmatch = 0
                min_num -= length_tolerance
                for tp in segtps:
                    t1_order_num = tp.order_num
                    match = get_matching_points(tp,tr2_id,min_num,[x[1] for x in matches]+t2_exclude_list,length_tolerance)
                    if match == {}:
                        n_unmatch += 1
                        if n_unmatch > length_tolerance/2:
                            break
                    else:
                        matches.append((match.keys()[0].order_num, match.values()[0].order_num))
                        min_num = match.values()[0].order_num
                        n_unmatch=0
                if len(matches) > length_tolerance:
                    matching_segments.append(matches)
                    t2_exclude_list += [x[1] for x in matches]
                matches = []

    return matching_segments

start = datetime.now()
print(start)
run_test()
end = datetime.now()
print(end)
print('total time spent: ' + str(end - start))
