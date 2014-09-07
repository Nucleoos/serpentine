# coding: utf-8
# Create your views here.
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.context_processors import csrf
# from django.core.mail import send_mail
from django.http import HttpResponseRedirect
# from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

import json
import datetime
# import re
import gps.settings
from gps import utils

from gps.models import Trace, Trace_point, Trace_property
from gps.forms import TrackForm, UploadForm, QuickLoginForm, QuickSearchForm

#import urls 

#Main context processor (defined in settings.py)
def main_context(request):
    d = {}
    #dernières traces 
    d['latest_traces'] = Trace.objects.all().order_by('-tdate')[0:10]
    #TODO get all properties

    #search context
    if request.method == 'GET' and request.GET.has_key('recherche'):
        d['quick_search_form'] = QuickSearchForm(request.GET)
    else:
        d['quick_search_form'] = QuickSearchForm()
    #login context
    if request.user.is_authenticated():
        d['user_logged'] = request.user.username
        d['mes_traces'] = Trace.objects.filter(user=User.objects.get(username=request.user.username)).order_by('-tdate')[0:10]
        upload_form = UploadForm()
        d['upload_form'] = upload_form
    else:
        if request.method == 'POST':
            d['login_form'] = QuickLoginForm(request.POST)
        else:
            d['login_form'] = QuickLoginForm()

    d.update(csrf(request))  #gestion protection csrf
    return d


#html pages 
def index(request):
    d = {}
    d['all_traces'] = Trace.objects.all().order_by('-tdate')
    return render_to_response(utils.get_prefix(request) + 'index.html', d, context_instance=RequestContext(request))


def view_trace(request, num):
    c = {}
    c['num'] = num
    cookies = request.COOKIES
    if cookies.has_key('maptype'):
        maptype = cookies['maptype']
    else:
        maptype = "ol"
    c['maptype'] = maptype
    tr = Trace.objects.get(id=num)
    c['trace'] = tr
    for p in tr.get_str_properties():
        c[p.name] = p.value
    c['ign_api_key'] = gps.settings.IGN_API_KEY
    ppt = tr.get_properties()
    for p in ppt:
        c[p] =[ppt[p]]
    response = render_to_response(utils.get_prefix(request) + 'trace.html', c, context_instance=RequestContext(request))
    #rafraichissement du cookie
    response.set_cookie(key='maptype', value=maptype, max_age=3600 * 24 * 30, expires=None, path='/', domain=None,
                        secure=None)
    return response


def recherche(request):
    c = {}
    if request.method == 'GET' and request.GET.has_key('recherche'):
        c['resultats'] = Trace.get_search_results(request.GET['recherche'])
        c['criteria'] = request.GET['recherche']
    rsp = render_to_response(utils.get_prefix(request) + 'recherche.html', c, context_instance=RequestContext(request))
    return rsp


#html ajax
def trace_info_html(request, num):
    c = {}
    c['num'] = num
    tr = Trace.objects.get(id=num)
    c['trace'] = tr
    for p in tr.get_str_properties():
        c[p.name] = p.value
    c['properties'] = tr.get_properties()
    return render_to_response('gps/traceinfo.html', c)


def trace_short_info_html(request, num):
    c = {}
    c['num'] = num
    tr = Trace.objects.get(id=num)
    c['trace'] = tr
    ppt = tr.get_str_properties('distance')
    return render_to_response('gps/traceshortinfo.html', c)

def trace_tabs_html(request, traces , segments=None):
    c = {'traces':traces}
    traces = traces.split('/')[1:] #le premier argument est 'traces'

    #initialisation du tableau des propriétés avec la première trace
    ppt = Trace.objects.get(id=int(traces[0])).get_properties()
    for p in ppt:
        c[p] = []
    #alimentation des propriétés pour le tableau
    for num in traces:
        ppt = Trace.objects.get(id=int(num)).get_properties()
        for p in ppt:
            c[p].append(ppt[p])


    if segments != None:
        segments = segments.split('/')[1:] #l'indice 0 est segment
        tr = Trace.objects.get(id=int(segments[0]))
        ppt = tr.get_segment_properties(segments[1],segments[2])
        for p in ppt:
            c[p].append(ppt[p])

    return render_to_response('gps/tracetabs.html', c)

def trace_stats(request, num):
    c = {}
    c['num'] = num
    tr = Trace.objects.get(id=num)
    c['trace'] = tr
    c['stats'] = tr.get_stats()
    return render_to_response('gps/tracestats.html', c)

def nav_html(request):
    """ renvoie le block des liens de navigation des traces interieurs aux bounds de la requete si appel ajax avec bounds
    """
    c = {}
    if request.method == 'GET':
        #TODO tester l'existence des cles
        minlat = float(request.GET['minlat'])
        minlon = float(request.GET['minlon'])
        maxlat = float(request.GET['maxlat'])
        maxlon = float(request.GET['maxlon'])
    trsin = Trace.get_tracks_in_bounds(minlat, minlon, maxlat, maxlon)
    if request.user.is_authenticated():
        usr = User.objects.get(username=request.user.username)
        c['latest_traces'] = trsin.order_by('-tdate')[:10]
        c['mes_traces'] = trsin.filter(user=usr).order_by('-tdate')[:10]
    else:
        c['latest_traces'] = trsin[:10]
    return render_to_response('gps/nav.html', c)


def nearby(request):
    c = {}
    lat, lon , tr_id = 0 ,0 ,0
    if request.method == 'GET':
        #DONE tester l'existence des cles
        lat, lon, tr_id = 0,0,0
        if request.GET.has_key('lat'):
            lat = float(request.GET['lat'])
        if request.GET.has_key('lon'):
            lon = float(request.GET['lon'])
        if request.GET.has_key('tr_id'):
            tr_id = int(request.GET['tr_id'])
    closest = Trace.get_closest_tracks(tr_id, lat, lon)
    c['closest_tracks'] = closest
    c['tr_id'] = tr_id
    return render_to_response('gps/nearby.html', c)


@cache_page(86400*365)
def gpx(request, num):
    response = HttpResponse(mimetype='text/gpx+xml')
    trace = Trace.objects.get(id=int(num))
    points = trace.get_points()
    lat = [p['lat'] for p in points]
    c = Context({'trace': trace.name, 'lat': lat, 'points': points})
    t = loader.get_template('gps/trace.gpx')
    response['Content-Disposition'] = 'attachment; filename="'+trace.name.encode('ascii','ignore')+'.gpx"'
    response.write(t.render(c))
    return response

#upload file
@login_required
def upload(request):
    """ vue qui charge les fichiers de trace depuis un fichier externe gpx, kml     """

    def handle_uploaded_file(f):
        destination = open(settings.MEDIA_ROOT + 'import.gpx', 'w')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        # on enregistre un minimum sur l'entête de trace pour pouvoir enrgistrer les points
        tr = Trace()
        tr.user = User.objects.get(username=request.user.username)
        tr.name = f.name
        tr.ctime = datetime.datetime.now()
        tr.save()
        tr.create_from_file(settings.MEDIA_ROOT + 'import.gpx')
        tr.save()
        return tr

    if request.user.is_authenticated():
        c = {}
        if request.method == 'POST':
            upload_form = UploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                cd = upload_form.cleaned_data
                tr = handle_uploaded_file(request.FILES['fichier'])
                tr.set_calculated_properties()
                tr.set_geonames_properties()
                return HttpResponseRedirect('/trace/' + unicode(tr.id))
        else:
            upload_form = UploadForm()
        c['upload_form'] = upload_form
        return render_to_response('gps/upload.html', c, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/login/')


def edit(request, num):
    if request.user.is_authenticated():
        c = {}
        c['num'] = num
        tr = Trace.objects.get(id=num)
        if request.method == 'POST':
            track_form = TrackForm(request.POST)
            if track_form.is_valid():
                cd = track_form.cleaned_data
                tr.name = cd['title']
                for k in cd.keys():
                    pr = Trace_property.objects.filter(trace__id=num, name=k)
                    if len(pr) > 0:
                        pp = pr[0]
                    else:
                        pp = Trace_property()
                    pp.trace = tr
                    pp.name = k
                    pp.value = cd[k]
                    pp.save()
                tr.save()
                return HttpResponseRedirect('/trace/' + unicode(num))
        else:
            #TODO todo rechercher les informations en base
            tpr = Trace_property.objects.filter(trace=tr)
            init = {}
            init['title'] = tr.name
            for p in tpr:
                if p.name in ('type', 'description'): init[p.name] = p.value
            track_form = TrackForm(initial=init)

        c['track_form'] = track_form
        return render_to_response('gps/trackform.html', c, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/login/')


#modify des tracks points
def modify(request):
    if request.method == 'POST':
        track = request.POST['track']
        tr = Trace()
        tr.name = 'modified'
        tr.user = User.objects.get(username=request.user.username)
        tr.ctime = datetime.datetime.now()
        tr.save()
        points = json.loads(track)
        tr.create_from_array(points)
        return HttpResponseRedirect('/trace/' + unicode(tr.id) + '/')
    else:
        return HttpResponseRedirect('/trace/1')


#login logout and register
def register(request):
    c = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()
    c['form'] = form
    #d.update(csrf(request)) #gestion protection csrf
    return render_to_response("gps/register.html", c, context_instance=RequestContext(request))


def login(request):
    if request.POST.__contains__('username'):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
    else:
        user = ''
    if user:
        auth.login(request, user)
    return HttpResponseRedirect("/")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


#javascript json
def view_trace_js(request, num, maptype):
    t = loader.get_template('gps/trace.js')
    c = {}
    c['num'] = num
    if maptype == None: maptype = "ol"
    c['maptype'] = maptype
    response = HttpResponse(t.render(Context(c)), mimetype='application/javascript')
    return response


@cache_page(86400*365)
def trace_json(request):
    if request.method == 'GET':
        t = int(request.GET['t'])
        points = Trace.objects.get(id=t).get_json()
        return HttpResponse(points, mimetype='application/javascript')


def trace_json_info(request):
    if request.method == 'GET':
        t = int(request.GET['t'])
        points = Trace.objects.get(id=t).get_json_info()
        return HttpResponse(points, mimetype='application/javascript')

@cache_page(1)
def trace_segment_json(request):
    if request.method == 'GET':
        if request.GET.has_key('t1') and request.GET.has_key('t2'):
            t1 = int(request.GET['t1'])
            t2 = int(request.GET['t2'])
            points = Trace.objects.get(id=t1).get_matching_segments_json(t2)
            return HttpResponse(points, content_type='application/javascript')
    return HttpResponse('{error}', content_type='application/javascript' )


def trace_json_index(request):
    #    if request.method == 'GET':
    traces = Trace.objects.all()
    index = {}
    bounds = {}
    bounds['minlon'], bounds['minlat'], bounds['maxlon'], bounds['maxlat'] = 180, 180, -180, -180
    for t in traces:
        fp = t.get_first_point()
        index[t.id] = {'id': t.id, 'name': t.name, 'lon': fp.longitude, 'lat': fp.latitude}
        if bounds['minlon'] > fp.longitude: bounds['minlon'] = fp.longitude
        if bounds['minlat'] > fp.latitude: bounds['minlat'] = fp.latitude
        if bounds['maxlon'] < fp.longitude: bounds['maxlon'] = fp.longitude
        if bounds['maxlat'] < fp.latitude: bounds['maxlat'] = fp.latitude
    index.update(bounds)
    return HttpResponse(json.dumps(index), mimetype='application/javascript')


def set_maptype(request, maptype):
    response = HttpResponse('')
    response.set_cookie(key='maptype', value=maptype, max_age=85000, expires=None, path='/', domain=None, secure=None)
    return response


# tests 
def test_cookies(request):
    """test des cookies 
    """
    c = {}
    c['request'] = request
    resp = render_to_response('gps/test_cookies.html', c)
    return resp


def test_ign(request):
    """ tests api ign
    """
    c = {}
    c['request'] = request
    resp = render_to_response('gps/test_ign.html', c)
    return resp
    
