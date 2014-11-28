# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
# from django.conf import settings
import datetime
import lib
import geonames
import json
from django.db.models import Avg, Max, Min, Count
from django.db import transaction
from django.db.models import Q
# import zipfile
# import os
# from ftplib import FTP
import gps.settings
# Create your models here.


class Trace(models.Model):
    TRACE_TYPES = (('VEL','Vélo de route'), ('VTT','VTT'), ('CAP','Course à pied'), ('MAR','Marche'), ('AUT', 'Autre'))
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User)
    type = models.CharField(max_length=3,choices=TRACE_TYPES,default='CAP')
    parent = models.ForeignKey('self', null=True, blank=True)
    ctime = models.DateTimeField('auto_now_add')
    tdate = models.DateTimeField(null=True)

    def __unicode__(self):
        nb_points = Trace_point.objects.filter(trace=self).count()
        return unicode(self.id) + " " + self.name
        """+ " -dist =" + unicode(
            self.get_total_distance()) + self.user.username + " ( " + unicode(self.ctime) + ")" \
               + ' nb pts ' +unicode(nb_points) + 'total time ' + self.get_formatted_time()
        """

    @transaction.commit_manually
    def create_from_file(self, file):
        """ cree les elements (points) de la traces depuis un fichier
            met à jour la date de trace à la date de 
            TODO: créer une vraie date de début pour la trace  
        """
        try:
            points = lib.getPointsFromFile(file)
            for p in points:
                tp = Trace_point()
                tp.set_values(self, p)
                tp.save()
            if points[0].has_key('time'):
                self.tdate = points[0]['time']
            else:
                self.tdate = self.ctime
            self.save()
            transaction.commit()
        except:
            transaction.rollback()
            raise
        # zfile = zipfile.ZipFile(file+'.zip','w',compression=zipfile.ZIP_DEFLATED)
        # zfile.write(file,file)
        # zfile.close
        # os.remove(file)

    @transaction.commit_manually
    def create_from_array(self, points):
        """ cree les element depuis une tableau de points """
        for p in points:
            p['time'] = datetime.datetime.now()
        points = lib.setDistancesAndSpeeds(points)
        n = 1
        for p in points:
            tp = Trace_point()
            tp.set_values(self, p, 1, n)
            tp.save()
            n = n + 1
        self.save()
        transaction.commit()

    def set_property(self, pname, pvalue):
        """affecte une propriété"""
        pr = Trace_property.objects.filter(trace__id=self.id, name=pname)
        if len(pr) > 0:
            pp = pr[0]
        else:
            pp = Trace_property()
        pp.trace = self
        pp.name = pname
        pp.value = pvalue
        pp.save()

    @transaction.commit_manually
    def set_properties(self, with_geonames = True):
        """ (ré) affecte toutes les propriétés de la trace dans la base de donnée"""
        #on va chercher les propriétés du segment
        try:
            properties = self.get_segment_properties()
            for ppt in properties:
                self.set_property(ppt,properties[ppt])
            if with_geonames:
                self.set_geonames_properties()
            transaction.commit()
        except:
            transaction.rollback()
            raise
        return self

    @transaction.commit_manually
    def clear_properties(self, with_geonames = True):
        """ supprime toutes les propriétés de la trace dans la base de donnée"""
        try:
            ppts = Trace_property.objects.filter(trace = self);
            for p in ppts:
                p.delete()
            transaction.commit()
        except:
            transaction.rollback()
            raise
        return self


    def get_segment_properties(self,start=-1,end=-1):
        properties ={}
        tp = Trace_point.objects.filter(trace=self)
        if start>0:
            tp = tp.filter(order_num__gte = str(start))
        if end > 0:
            tp = tp.filter(order_num__lte = str(end))
        agg = tp.aggregate(Max("time"), Min("time"), Max("speed"),Avg("speed"),Max("elevation"),Min("elevation"),Max("distance"),Min("distance"),Min('latitude'), Max('latitude'),
                           Min('longitude'), Max('longitude'), Max('heartrate'), Min('heartrate'), Avg('heartrate'))
        properties['title'] =  'tr ' + str(self.id) + ' segment ('+str(start)+','+str(end)+')'
        properties['total_time'] = agg['time__max']-agg['time__min']
        properties['distance'] = agg['distance__max']-agg['distance__min']
        properties['max_elevation'] = agg['elevation__max']
        properties['min_elevation'] = agg['elevation__min']
        properties['amplitude_elevation'] = agg['elevation__max']-agg['elevation__min']
        properties['max_speed'] = agg['speed__max']
        properties['avg_speed'] = 3600*(agg['distance__max']-agg['distance__min'])/((agg['time__max']-agg['time__min']).seconds +(agg['time__max']-agg['time__min']).days*86400) if (agg['time__max']-agg['time__min']).seconds > 0 else 0
        properties['max_lat'] = agg['latitude__max']
        properties['min_lat'] = agg['latitude__min']
        properties['max_lon'] = agg['longitude__max']
        properties['min_lon'] = agg['longitude__max']
        properties['min_hr'] = agg['heartrate__min']
        properties['max_hr'] = agg['heartrate__max']
        properties['avg_hr'] = agg['heartrate__avg']
        return properties

    def get_properties(self, *args):
        """ récupère les propriétés de la trace et retourne un dict 
            renvoie tout si aucun argument n'est spécifié"""
        if args == ():
            ppt = Trace_property.objects.filter(trace=self)
        else:
            ppt = Trace_property.objects.filter(trace=self, name__in=args)
        return ppt

    def get_points(self):
        """ renvoie un tableau des points de la trace sous la forme d'un tableau de dictionaires"""
        tp = Trace_point.objects.filter(trace=self).order_by('time')
        points = []
        for p in tp:
            points.append(p.get_dict())
        return points

    def clear_points(self):
        tp = Trace_point.objects.filter(trace=self)
        for p in tp:
            p.delete()
            #propriétés calculées

    def get_total_distance(self):
        return Trace_point.objects.filter(trace=self).aggregate(Max("distance"))["distance__max"]

    def get_total_time(self):
        """ secondes """
        t = Trace_point.objects.filter(trace=self).aggregate(Max("time"), Min("time"))
        td = t["time__max"] - t["time__min"]
        return td

    def get_max_speed(self):
        return Trace_point.objects.filter(trace=self).aggregate(Max("speed"))["speed__max"]

    def get_elevation_amplitude(self):
        return Trace_point.objects.filter(trace=self).aggregate(Max("elevation"))["elevation__max"] - \
               Trace_point.objects.filter(trace=self).aggregate(Min("elevation"))["elevation__min"]

    def get_elevation_max(self):
        return Trace_point.objects.filter(trace=self).aggregate(Max("elevation"))["elevation__max"]

    def get_elevation_min(self):
        return Trace_point.objects.filter(trace=self).aggregate(Min("elevation"))["elevation__min"]

    def set_geonames_properties(self):
        """Renvoie les villes traversées (depuis geonames.org api postal codes) 
           Alimente les propriétés de la trace avec (Ville de départ, villes traversées etc.)
        """
        import urllib
        import simplejson as json

        pts = self.get_points()
        #villes de départ et d'arrivée
        fp = pts[0]
        depart = geonames.getClosestTown(fp['lat'], fp['lon'])
        self.set_property('depart', depart)
        lp = pts[len(pts) - 1]
        arrivee = geonames.getClosestTown(lp['lat'], lp['lon'])
        self.set_property('arrivee', arrivee)
        # via step points step = 20 
        step, vias, vs = 15, [], ''
        if len(pts) > step * 2:
            for i in range(len(pts) / step, len(pts) - len(pts) / step, len(pts) / step):
                v = geonames.getClosestTown(pts[i]['lat'], pts[i]['lon'])
                if v not in vias and v not in (depart, arrivee): vias.append(v)
            for i in vias: vs = vs + i + ', '
            if len(vs) - 2 > 255: vs = vs[0:257]
            self.set_property('vias', vs[0:len(vs) - 2])
        return vs

    #getters information traces

    def get_bounds(self):
        #pts = self.getPoints()
        return Trace_point.objects.filter(trace=self).aggregate(Max('latitude'), Min('latitude'), Max('longitude'),
                                                                Min('longitude'))

    def get_first_point(self):
        return Trace_point.objects.filter(trace=self).order_by('order_num')[0]

    def get_last_point(self):
        return Trace_point.objects.filter(trace=self).order_by('-order_num')[0]

    def get_avg_lat_lon(self):
        """Renvoie la latitude et longitude "moyenne" de la trace (dictionnary{lat,lon}
        """
        p = Trace_point.objects.filter(trace=self).aggregate(Avg("latitude"), Avg("longitude"))
        return {'lat': p["latitude__avg"], 'lon': p["longitude__avg"]}

    #TODO supprimer
    def get_info(self):
        """ get un dictionnaire for quick info on the Trace object"""
        tr = {"id": self.id, "name": self.name, "total_time": self.get_total_time().seconds,
              "total_distance": str(round(self.get_total_distance(), 2)) ,
              "avg_speed": str(round(self.get_avg_speed(), 1))}
        tr.update(self.get_bounds())
        return tr

    def get_json(self):
        """ get json format of the Trace object"""
        tr = {"name": self.name, "total_time": str(self.get_total_time()), "total_distance": self.get_total_distance(),
              "avg_speed": self.get_avg_speed()}
        tr["points"] = self.get_points()
        return json.dumps(tr)

    def get_json_info(self):
        """ get json format for quick info on the Trace object"""
        return json.dumps(self.get_info())

    def get_matching_segments_old(self, tr2_id):
        """ repérage et TODO: stockage des segments communs entre self et tr2
        on passe une tolerance en longueur pour le match (plus c'est élevé plus on tolère de mismatchs
        TODO: stockage en base des repérages de segments matchés
        TODO: search_small_step est le levier d'amélioration dans le paramétrage
        """
        search_big_step = 30  # nombre de points entre 2 tests en recherche grosse maille
        search_small_step = 1  # nombre de points entre 2 tests après avoir trouvé le premier match
        dist_tolerance = 0.040
        min_seg_dist = 0.300 # 300m
        mismatch_tolerance = 5 #tolerance de perte de chemin commun  en nombre de points
        lonlat_delta = 10
        seg2_search_length = 100 #range of points to be search further after first match found

        #DONE: use excluded ranges instead of excluded lists
        def get_matching_points(tp1 ,tr2_id, num_min = 0, exclude_list = []):
            """ renvoie pour tp1 les points de t2 susceptible de matcher les points de t1
                avec un order_num >= à order_min
            """
            match = {}
            tps = Trace_point.objects.filter(trace=tr2_id)
            if num_min != 0:
                tps = tps.filter(order_num__lt = num_min + seg2_search_length)
            if len(exclude_list)>950:
            #handling sqlite limitations (but exclude list should not be so long) i should use excluded_ranges cf previous to do.
            # this is artificially introducing a maxlength to the matching segment
                return {}
            tps = tps.filter(order_num__gt = num_min).exclude(order_num__in=exclude_list)
            tps = tps.extra(where=['10000*(abs('+str(tp1.latitude)+'-latitude)+abs('+str(tp1.longitude)+'-longitude)) <'+str(lonlat_delta)])
            tps = tps.order_by('order_num')
            # print tps.query
            if tps.count()>0:
                min_dist = 1 #on commence avec 1 km
                tp2 = tps[0]
                for t in tps:
                    #dist = lib.getDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                    dist = lib.getQuickDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                    if dist < min_dist:
                        min_dist = dist
                        tp2 = t
                if min_dist < dist_tolerance:
                    match[tp1] = tp2
                else:
                    return {}
            return match

        tps = Trace_point.objects.filter(trace=self)[::search_big_step] #query with a step equals to tolerance
        matches = [] #liste de points matchants
        t1_order_num = 0
        exclude_list = [] #liste des points déjà matchés dans t2=> à exclure
        matching_segments = [] #liste de matches dont la longueur est suffisante
        for tp1 in tps:
            if tp1.order_num > t1_order_num:
                t1_order_num = tp1.order_num
                match = get_matching_points(tp1, tr2_id, 0, exclude_list)
                if match != {}:
                    # matches.append((match.keys()[0].order_num, match.values()[0][0].order_num))
                    t2_min_num = match.values()[0].order_num-search_big_step
                    t1_order_num = t1_order_num-search_big_step
                    # try to build a segment ( with first match, i go back search_step points) and find the first matching point
                    segtps = Trace_point.objects.filter(trace=self).filter(order_num__gt=t1_order_num)
                    n_unmatch , first_match_found = 0,0
                    #boucle en small step
                    for tp in segtps[::search_small_step]:
                        match = get_matching_points(tp,tr2_id,t2_min_num-search_small_step,exclude_list)
                        if match == {}:
                            n_unmatch += 1
                            if n_unmatch > mismatch_tolerance and first_match_found==1:
                                break
                        else:
                            matches.append((match.keys()[0].order_num, match.values()[0].order_num))
                            t2_min_num = match.values()[0].order_num
                            n_unmatch, first_match_found=0,1

                    if len(matches) > 0:
                        start = Trace_point.objects.filter(trace= self).filter(order_num = matches[0][0])[0]
                        end = Trace_point.objects.filter(trace= self).filter(order_num = matches[-1][0])[0]
                        dist_seg = lib.getDistance(start.latitude,start.longitude, end.latitude, end.longitude)
                        if dist_seg > min_seg_dist:
                            matching_segments.append(matches)
                            if len(matches) >0: exclude_list += range(matches[0][1],matches[-1][1])
                        matches = []

        return matching_segments

    def get_matching_segments(self, tr2_id):
        """ repérage et TODO: stockage des segments communs entre self et tr2
        on passe une tolerance en longueur pour le match (plus c'est élevé plus on tolère de mismatchs
        TODO: stockage en base des repérages de segments matchés
        TODO: search_small_step est le levier d'amélioration dans le paramétrage
        """
        search_big_step = 30# nombre de points entre 2 tests en recherche grosse maille
        search_small_step = 2 # nombre de points entre 2 tests après avoir trouvé le premier match
        dist_tolerance = 0.030
        min_seg_dist = 0.300 # 300m
        mismatch_tolerance = 2 #tolerance de perte de chemin commun  en nombre de points
        lonlat_delta = 10
        seg2_search_length = 100 #range of points to be search further after first match found

        def get_matching_points(tp1 ,tr2_id,  excluded_ranges=''):
            """ renvoie pour tp1 les points de t2 susceptible de matcher les points de t1
                avec un order_num >= à order_min
            """
            match = {}
            tps = Trace_point.objects.filter(trace=tr2_id).order_by('order_num')
            # if num_min != 0:
            #     tps = tps.filter(order_num__lt = num_min + seg2_search_length)
            #tps = tps.filter(order_num__gt = num_min)
            if excluded_ranges != '':
                excluded_ranges = 'not (' +excluded_ranges[0:-4] +')'
                tps = tps.extra(where=[excluded_ranges])
            tps = tps.extra(where=['10000*(abs('+str(tp1.latitude)+'-latitude)+abs('+str(tp1.longitude)+'-longitude)) <'+str(lonlat_delta)])
            tps = tps.order_by('order_num')
            # print tps.query
            if tps.count()>0:
                min_dist = 1 #on commence avec 1 km
                tp2 = tps[0]
                for t in tps:
                    #dist = lib.getDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                    dist = lib.getQuickDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                    if dist < min_dist:
                        min_dist = dist
                        tp2 = t
                if min_dist < dist_tolerance:
                    match[tp1] = tp2
                else:
                    return {}
            return match

        tps = Trace_point.objects.filter(trace=self).order_by('order_num')[::search_big_step] #query with a step equals to tolerance
        matches = [] #liste de points matchants
        t1_order_num = 0
        range_extra=''
        matching_segments = [] #liste de matches dont la longueur est suffisante
        for tp1 in tps:
            if tp1.order_num > t1_order_num:
                t1_order_num = tp1.order_num
                match = get_matching_points(tp1, tr2_id, range_extra)
                if match != {}:
                    # matches.append((match.keys()[0].order_num, match.values()[0][0].order_num))
                    t1_order_num = t1_order_num-search_big_step
                    segtps = Trace_point.objects.filter(trace=self).filter(order_num__gt=t1_order_num)
                    n_unmatch , first_match_found = 0,0
                    #boucle en small step
                    for tp in segtps[::search_small_step]:
                        match = get_matching_points(tp,tr2_id,range_extra)
                        if match == {}:
                            n_unmatch += 1
                            if n_unmatch > mismatch_tolerance and first_match_found==1:
                                break
                        else:
                            matches.append((match.keys()[0].order_num, match.values()[0].order_num))
                            n_unmatch, first_match_found=0,1

                    if len(matches) > 0:
                        start = Trace_point.objects.filter(trace= self).filter(order_num = matches[0][0])[0]
                        end = Trace_point.objects.filter(trace= self).filter(order_num = matches[-1][0])[0]
                        dist_seg = lib.getDistance(start.latitude,start.longitude, end.latitude, end.longitude)
                        if dist_seg > min_seg_dist:
                            matching_segments.append(matches)
                            t1_order_num = matches[-1][0] +1  # on reprendra au dernier point matché sur t1
                            if len(matches) >0:
                                range_extra += '(order_num >' + str(matches[0][1]) +' and order_num <'+str(matches[-1][1])+') or '
                        matches = []
        return matching_segments

    def get_matching_segments_json(self, tr2_id):
        """ get json for matching segments as Trace format """
        start = datetime.datetime.now()
        segments = self.get_matching_segments(tr2_id)
        td = (datetime.datetime.now() - start)
        time_spent ="%d.%d" % (td.seconds, td.microseconds/10000)
        tr = []
        for i, seg in enumerate(segments):
            s = {}
            tp = Trace_point.objects.filter(trace=self).filter(order_num__gt=seg[0][0])
            tp = tp.filter(order_num__lt=seg[-1][0]).order_by('time')
            points = []
            for p in tp:
                points.append(p.get_dict())
            s['time_spent'] = time_spent
            s['points'] = points
            tr.append(s)
        return json.dumps(tr)


    #traitements sur les points de la trace
    @transaction.commit_manually
    def compute_distances(self):
        """ compute distances from the first point to the last point """
        current_lat, current_lon = 0.0, 0.0
        dist = 0
        x, t = 0, 0
        tp = Trace_point.objects.filter(trace=self).order_by('time')
        for p in tp:
            x = lib.getDistance(current_lat, current_lon, p.latitude, p.longitude)
            dist = dist + x
            p.distance = dist
            p.save()
            current_lat = p.latitude
            current_lon = p.longitude
        transaction.commit()

    @transaction.commit_manually
    def compute_speeds(self):
        """ compute instant speed for every point of the Trace object  """
        tp = Trace_point.objects.filter(trace=self).order_by('time')
        for p in tp:
            if p.distance == 0 or p1.distance == 0:
                p1, p2 = p, p
                p0 = p1
                p1.speed, t = 0, p.time
                p1.save()
            else:
                p2 = p
                td = p2.time - p0.time  # td = timedelta
                if td.seconds > 0:
                    p1.speed = 3600 * (p2.distance - p0.distance) / td.seconds
                else:
                    p1.speed = p0.speed
                p1.save()
                p0 = p1
                p1 = p2
        transaction.commit()

    #getters
    def get_avg_speed(self):
        tp = Trace_point.objects.filter(trace=self).order_by('time')
        dist = tp[tp.count() - 1].distance
        td = tp[tp.count() - 1].time - tp[0].time
        tt = self.get_total_time().seconds
        if tt == 0:
            return 0
        return 3600 * dist / (self.get_total_time().seconds + self.get_total_time().days*86400)

    def get_stats(self):
        total_time = self.get_total_time().seconds
        total_distance = self.get_total_distance()
        stats = {
            'distance':total_distance,
            'seconds':total_time,
            'allure': total_time/total_distance,
            'speed': 3600*total_distance/total_time
        }
        return stats

    def get_bests(self, forcecalc = False):
        dists = [('best 100m',0.1),
                 ('best 400m',0.4),
                 ('best km',1),
                 ('best 2 km',2),
                 ('best 5km',5),
                 ('best 10km',10),
                 ('best 20km',20),
                 ('best 50km',50),
                 ]
        best=[]
        for d in dists:
            if d[1] <= self.get_total_distance():
                #TODO recherche préalable dans les records de la trace précédent calcul
                trec = Trace_record.objects.filter(trace = self).filter(type = d[0])
                if forcecalc or trec.count() == 0:
                    #print 'calcul '+ d[0]
                    bestperf = self.get_best_performances(d[1])
                    if bestperf != None:
                        best.append((d[0], bestperf))
                        tr = Trace_record()
                        tr.trace, tr.type, tr.distance, tr.seconds = self, d[0], bestperf['dist'], bestperf['seconds']
                        tr.start, tr.end = bestperf['start'], bestperf['end']
                        tr.save()
                else:
                    #print 'lecture', ppt[0].name
                    best.append((trec[0].type, {'dist':trec[0].distance, 'seconds':trec[0].seconds,
                                                'allure': trec[0].seconds/trec[0].distance,
                                                'speed': 3600*trec[0].distance/trec[0].seconds,
                                                'start': trec[0].start, 'end': trec[0].end}))
        return best

    def get_best_performances(self,distbest):
        """
        Calcule la meilleure portion de distbest sur la trace par un parcours + ou - optimisé (dychotomie)
        :param distance: distance du best (400m 1km 1 mile . etc)
        :return: dictionnary meilleur temps, index first point , index last point
        """
        tps = [tp for tp in Trace_point.objects.filter(trace=self).order_by('order_num')]
        start, end , besttime = 0, tps[-1].order_num-1, (tps[-1].time - tps[0].time).seconds
        result = None
        if distbest > tps[-1].distance:
            return None
        # On recherche d'abord le premier tronçon qui correspond à la distance recherchée
        notfound = True
        jumpsize = end/2
        while(notfound):
            while(tps[end].distance - tps[start].distance >= distbest):
                end = end - jumpsize
                if jumpsize > 1:
                    jumpsize = jumpsize/2
                else:
                    notfound = False
                    result = {'start':start, 'end':end, 'dist':tps[end].distance- tps[start].distance, 'seconds':(tps[end].time- tps[start].time).seconds}
                    break
            if jumpsize > 1:
                jumpsize = jumpsize /2
            else:
                result = {'start':start, 'end':end, 'dist':tps[end].distance- tps[start].distance, 'seconds':(tps[end].time- tps[start].time).seconds}
                break
            while(notfound  and tps[end].distance - tps[start].distance < distbest):
                end = end+jumpsize
                if  end > tps[-1].order_num-1: end = tps[-1].order_num-1
                #print end, tps[end].distance
            jumpsize = jumpsize/2
        # sortis de la boucle on a un result non vide qui sert de base à la suite sinon on retourne None
        if result != None:
            start , end, besttime  = result['start'], result['end'], result['seconds']
            while start < tps[-1].order_num-1 and end < tps[-1].order_num-1:
                start +=1
                while(tps[end].distance - tps[start].distance <= distbest):
                    if end < tps[-1].order_num-1:
                        end+=1
                    else: break
                if tps[end].distance - tps[start].distance >= distbest:
                    if (tps[end].time- tps[start].time).seconds < besttime:
                        besttime = (tps[end].time- tps[start].time).seconds
                        result = {'start':start, 'end':end, 'dist':tps[end].distance- tps[start].distance, 'seconds':besttime}

        result['allure']= int(result['seconds']/result['dist'])
        result['speed']=3600*result['dist']/result['seconds']
        return result

    def set_start_date_from_first_point(self):
        firsttp = Trace_point.objects.filter(trace=self).order_by('time')[0]
        self.tdate = firsttp.time

        #méthodes statiques


    @staticmethod
    def get_tracks_in_bounds(minlat, minlon, maxlat, maxlon):
        trs = Trace.objects.filter(trace_point__order_num=1, trace_point__latitude__gt=minlat,
                                   trace_point__latitude__lt=maxlat, trace_point__longitude__gt=minlon,
                                   trace_point__longitude__lt=maxlon).order_by('-ctime')
        return trs

    @staticmethod
    def get_closest_tracks(tr_id, lat, lon):
        """Renvoie les traces les plus proches du point passé en paramètre
            à l'exception de tr_id (trace courante)
           Calcul fait sur la base du point "moyen" des traces
        """
        #boundbox progressivement agrandie, on s'arrete quand on a plus de 10 traces, on les ordonne par distance puis on renvoie les 10 premiers
        boxsize, trs, trsdis = gps.settings.SEARCH_BOX_SIZE, [], []
        #TODO optimiser ?
        while len(trs) < 10 and boxsize < 2000:
            boxsize = boxsize * 2 + gps.settings.SEARCH_BOX_SIZE  #on augmente de plus en plus vite
            trs = Trace.get_tracks_in_bounds(lat - boxsize, lon - boxsize, lat + boxsize, lon + boxsize)
        #recherche des 10 plus proches
        #trsdis = [(t,lib.getDistanceAB(lat,lon,t.getFirstPoint().latitude,t.getFirstPoint().longitude)) for t in trs]
        for t in trs:
            if t.id != tr_id:
                avgPt = t.get_avg_lat_lon()
                trsdis.append((t, lib.getDistance(lat, lon, avgPt['lat'], avgPt['lon'])))
        trs = sorted(trsdis, key=lambda trk: trk[1])[0:10]
        return trs


    @staticmethod
    def get_search_results(criteria):
        """renvoie les traces ré&pondant aux critères
        Arguments:
        - `criteria`: pour l'instant une chaine de caractères
        """
        trs = Trace.objects.filter(trace_property__value__icontains=criteria).distinct()
        res = [{'type': 'Parcours', 'id': tr.id, 'nom': tr.name,
                'properties': tr.get_properties('description', 'depart', 'arrivee', 'vias')} for tr in trs]
        return res


#Class Trace_point
class Trace_point(models.Model):
    trace = models.ForeignKey(Trace)
    segment = models.IntegerField()
    order_num = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    time = models.DateTimeField()
    elevation = models.FloatField(null=True)
    distance = models.FloatField(null=True)
    speed = models.FloatField(null=True)
    heading = models.IntegerField(null=True)
    heartrate = models.IntegerField(null=True)
    cadence = models.IntegerField(null=True)
    power = models.IntegerField(null=True)
    temperature = models.IntegerField(null=True)
    pression = models.IntegerField(null=True)

    def __unicode__(self):
        u = "tr" + unicode(self.trace.id)
        u = u + " / seg:" + unicode(self.segment)
        u = u + " / num:" + unicode(self.order_num) + " / lat: " + unicode(self.latitude) + " / lon:" + unicode(self.longitude)
        u = u + " / ele: " + unicode(self.elevation)
        u = u + " / time: " + unicode(self.time)
        u = u + " / dist: " + unicode(self.distance)
        u = u + " / speed: " + unicode(self.speed)
        u = u + " / hr: " + unicode(self.heartrate)
        return u

    def set_values(self, trace, point):
        """ initialise les elements de Trace point avec un dictionnaire """
        self.trace = trace
        self.latitude = point['lat']
        self.longitude = point['lon']
        self.time = point['time']
        self.segment = point['segment']
        self.order_num = point['order_num']
        if point.has_key('elevation'):
            self.elevation = point['elevation']
        if point.has_key('distance'):
            self.distance = point['distance']      
        if point.has_key('speed'):
            self.speed = point['speed']
        if point.has_key('heading'):
            self.heading = point['heading']
        if point.has_key('heartrate'):
            self.heartrate = point['heartrate']
        if point.has_key('cadence'):
            self.cadence = point['cadence']
        if point.has_key('power'):
            self.power = point['power']
        if point.has_key('temperature'):
            self.temperature = point['temperature']
        if point.has_key('pression'):
            self.pression = point['pression']


    def get_dict(self):
        """ renvoie le dictionnaire de la trace_point """
        d = {'lat': self.latitude, 'lon': self.longitude, 'ele': self.elevation, 'time': self.time.isoformat() + "Z",
             'speed': self.speed, 'dist': self.distance}
        return d


class Trace_property(models.Model):
    trace = models.ForeignKey(Trace)
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=255)
    def __unicode__(self):
        return 'tr' + unicode(self.trace.id) + ' ' + self.name + ': ' + self.value

class Trace_record(models.Model):
    trace = models.ForeignKey(Trace)
    start = models.IntegerField()
    end = models.IntegerField()
    type = models.CharField(max_length=255) # best 100, 200, etc
    seconds = models.FloatField()
    distance = models.FloatField()

    def __unicode__(self):
        return self.type + ' ' + self.trace.name + ' ' +unicode(self.seconds) + ' secs'

    @staticmethod
    def get_all_records():
        return Trace_record.objects.all()


class Trace_point_property(models.Model):
    trace_point = models.ForeignKey(Trace_point)
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=255)
    def __unicode__(self):
        return 'Property trace:'+unicode(self.trace_point.trace.id)+' tp_ord:' + unicode(self.trace_point.order_num) + ': ' + self.name + ': ' + self.value

class User_profile(models.Model):
    user = models.ForeignKey(User)
