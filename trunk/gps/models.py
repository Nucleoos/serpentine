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
# import zipfile
# import os
# from ftplib import FTP
import gps.settings
# Create your models here.


class Trace(models.Model):
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User)
    parent = models.ForeignKey('self', null=True, blank=True)
    ctime = models.DateTimeField('auto_now_add')
    tdate = models.DateTimeField(null=True)

    def __unicode__(self):
        nb_points = Trace_point.objects.filter(trace=self).count()
        return unicode(self.id) + " " + self.name + " -dist =" + unicode(
            self.get_total_distance()) + self.user.username + " ( " + unicode(self.ctime) + ")" + ' nb pts ' +unicode(nb_points)

    @transaction.commit_manually
    def create_from_file(self, file):
        """ cree les elements (points) de la traces depuis un fichier kml Mercury100 ou gpx
            met à jour la date de trace à la date de 
            TODO: créer une vraie date de début pour la trace  
        """
        points = lib.getPointsFromFile(file)
        n = 1
        for p in points:
            tp = Trace_point()
            tp.set_values(self, p, 1, n)
            tp.save()
            n += 1
        transaction.commit()
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

    def set_calculated_properties(self):
        """ affecte toutes les propriétés calculées de la trace"""
        self.set_property('distance', str(round(self.get_total_distance(), 2)) + ' km')
        self.set_property('total_time', self.get_formatted_time())
        self.set_property('avg_speed', str(round(self.get_avg_speed(), 2)) + " km/h")
        self.set_property('max_speed', str(round(self.get_max_speed(), 2)) + " km/h")
        self.set_property('ele_amplitude', str(round(self.get_elevation_amplitude(), 0)) + " m")
        self.set_property('ele_max', str(round(self.get_elevation_max(), 0)) + " m")
        self.set_property('ele_min', str(round(self.get_elevation_min(), 0)) + " m")
        return 'done'  #self.getProperties()

    def get_properties(self, *args):
        """ récupère les propriétés de la trace et retourne un dict 
            renvoie tout si aucun argument n'est spécifié"""
        if args == ():
            return Trace_property.objects.filter(trace=self)
        else:
            return Trace_property.objects.filter(trace=self, name__in=args)

    def get_points(self):
        """ renvoie un tableau des points de la trace sous la forme d'un tableau de dictionaires"""
        tp = Trace_point.objects.filter(trace=self).order_by('time')
        points = []
        for p in tp:
            points.append(p.get_dict())
        return points

    def get_points_new(self):
        """ renvoie un tableau des points de la trace sous la forme d'un tableau de dictionaires"""
        tp = Trace_point.objects.filter(trace=self).order_by('time').values()
        return tp

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
        return td.seconds + td.days * 24 * 3600

    def get_max_speed(self):
        return Trace_point.objects.filter(trace=self).aggregate(Max("speed"))["speed__max"]

    def get_elevation_amplitude(self):
        return Trace_point.objects.filter(trace=self).aggregate(Max("elevation"))["elevation__max"] - \
               Trace_point.objects.filter(trace=self).aggregate(Min("elevation"))["elevation__min"]

    def get_elevation_max(self):
        return Trace_point.objects.filter(trace=self).aggregate(Max("elevation"))["elevation__max"]

    def get_elevation_min(self):
        return Trace_point.objects.filter(trace=self).aggregate(Min("elevation"))["elevation__min"]

    def get_formatted_time(self):
        """ chaine x jours etc """
        t = self.get_total_time()
        d = t / (3600 * 24)
        h = (t - d * 24 * 3600) / 3600
        m = (t - d * 24 * 3600 - h * 3600) / 60
        s = (t - d * 24 * 3600 - h * 3600 - m * 60)
        res = ''
        if d > 0: res = str(d) + 'j '
        if h > 0: res = res + str(h) + 'h '
        if m > 0: res = res + str(m) + 'm '
        res = res + str(s) + 's'
        return res

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

    def get_info(self):
        """ get un dictionnaire for quick info on the Trace object"""
        tr = {"id": self.id, "name": self.name, "total_time": self.get_formatted_time(),
              "total_distance": str(round(self.get_total_distance(), 2)) + " km",
              "avg_speed": str(round(self.get_avg_speed(), 2)) + " km/h"}
        tr.update(self.get_bounds())
        return tr

    def get_json(self):
        """ get json format of the Trace object"""
        tr = {"name": self.name, "total_time": self.get_total_time(), "total_distance": self.get_total_distance(),
              "avg_speed": self.get_avg_speed()}
        tr["points"] = self.get_points()
        return json.dumps(tr)

    def get_json_info(self):
        """ get json format for quick info on the Trace object"""
        return json.dumps(self.get_info())

    def get_matching_segments(self, tr2_id):
        """ repérage et TODO: stockage des segments communs entre self et tr2
        on passe une tolerance en longueur pour le match (plus c'est élevé plus on tolère de mismatchs
        TODO: stockage en base des repérages de segments matchés
        """
        search_step = 20  # nombre de points
        dist_tolerance = 0.040
        min_seg_dist = 0.100
        mismatch_tolerance = 40 #tolerance de distortion en nombre de points

        #TODO: use excluded ranges instead of excluded lists
        def get_matching_points(tp1 ,tr2_id, num_min = 0, exclude_list = []):
            """ renvoie pour tp1 les points de t2 susceptible de matcher les points de t1
                avec un order_num >= à order_min
            """
            match = {}
            tps = Trace_point.objects.filter(trace=tr2_id)
            if num_min != 0:
                tps = tps.filter(order_num__lt = num_min +2*search_step)
            if len(exclude_list)>950:
            #handling sqlite limitations (but exclude list should not be so long) i should use excluded_ranges cf previous to do.
            # this is artificially introducing a maxlength to the matching segment
                return {}
            tps = tps.filter(order_num__gt = num_min).exclude(order_num__in=exclude_list)
            tps = tps.extra(where=['10000*(abs('+str(tp1.latitude)+'-latitude)+abs('+str(tp1.longitude)+'-longitude)) < 10'])
            #todo approx plane for dist
            # tps = tps.extra(where=['power(3,2)<3'])
            tps = tps.order_by('order_num')
            # print tps.query
            if tps.count()>0:
                min_dist = 1 #on commence avec 1 km
                tp2 = tps[0]
                for t in tps:
                    dist = lib.getDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                    #dist = lib.getQuickDistance(tp1.latitude, tp1.longitude,t.latitude, t.longitude)
                    if dist < min_dist:
                        min_dist = dist
                        tp2 = t
                if min_dist < dist_tolerance:
                    match[tp1] = tp2
                else:
                    return {}
            return match

        tps = Trace_point.objects.filter(trace=self)[::search_step] #query with a step equals to tolerance
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
                    t2_min_num = match.values()[0].order_num-search_step
                    # try to build a segment ( with first match, i go back search_step points)
                    segtps = Trace_point.objects.filter(trace=self).filter(order_num__gt=t1_order_num-search_step)
                    n_unmatch = 0
                    for tp in segtps:
                        match = get_matching_points(tp,tr2_id,t2_min_num,exclude_list)
                        if match == {}:
                            n_unmatch += 1
                            if n_unmatch > mismatch_tolerance:
                                break
                        else:
                            matches.append((match.keys()[0].order_num, match.values()[0].order_num))
                            t2_min_num = match.values()[0].order_num
                            n_unmatch=0

                    if len(matches) > 0:
                        start = Trace_point.objects.filter(trace= self).filter(order_num = matches[0][0])[0]
                        end = Trace_point.objects.filter(trace= self).filter(order_num = matches[-1][0])[0]
                        dist_seg = lib.getDistance(start.latitude,start.longitude, end.latitude, end.longitude)
                        if dist_seg > min_seg_dist:
                            matching_segments.append(matches)
                            if len(matches) >0: exclude_list += range(matches[0][1],matches[-1][1])
                        matches = []

        return matching_segments

    def get_matching_segments_json(self, tr2_id):
        """ get json for matching segments as Trace format """
        segments = self.get_matching_segments(tr2_id)
        tr = []
        for i, seg in enumerate(segments):
            s = {}
            tp = Trace_point.objects.filter(trace=self).filter(order_num__gt=seg[0][0])
            tp = tp.filter(order_num__lt=seg[-1][0]).order_by('time')
            points = []
            for p in tp:
                points.append(p.get_dict())
            s['segment'] = i+1
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

    def get_avg_speed(self):
        tp = Trace_point.objects.filter(trace=self).order_by('time')
        dist = tp[tp.count() - 1].distance
        td = tp[tp.count() - 1].time - tp[0].time
        tt = self.get_total_time()
        if tt == 0:
            return 0
        return 3600 * dist / self.get_total_time()

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
    order_num = models.IntegerField(null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.FloatField(null=True)
    time = models.DateTimeField(null=True)
    distance = models.FloatField()
    speed = models.FloatField()
    segment_number = models.IntegerField()

    def __unicode__(self):
        u = "tr" + unicode(self.trace.id)
        u = u + " / order_num:" + unicode(self.order_num) + " / lat: " + unicode(self.latitude) + " / lon:" + unicode(self.longitude)
        u = u + " / elevation: " + unicode(self.elevation)
        u = u + " / time: " + unicode(self.time)
        u = u + " / distance: " + unicode(self.distance)
        u = u + " / speed: " + unicode(self.speed)
        return u

    def set_values(self, trace, point, segment_number, order_num):
        """ initialise les elements de Trace point avec un dictionnaire """
        self.trace = trace
        self.latitude = point['lat']
        self.longitude = point['lon']
        self.distance = point['distance']
        self.speed = point['speed']
        self.order_num = order_num
        if point.has_key('ele'):
            self.elevation = point['ele']
        if point.has_key('time'):
            self.time = point['time']
        self.segment_number = segment_number

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

