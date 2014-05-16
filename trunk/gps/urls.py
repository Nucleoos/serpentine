from django.conf.urls import patterns, include, url
#from views import *

urlpatterns = patterns('',
                       #APPLICATION gps
                       (r'^$', 'gps.views.index'),
                       (r'^recherche/$', 'gps.views.recherche'),
                       #gpx file
                       (r'^trace/(\d+).gpx', 'gps.views.gpx'),
                       #view_trace html
                       (r'^trace/(?P<num>\d+)$', 'gps.views.view_trace'),
                       (r'^traceinfo/(\d+)', 'gps.views.trace_info_html'),
                       (r'^traceshortinfo/(\d+)', 'gps.views.trace_short_info_html'),
                       (r'^tracetabs/(traces(?:/\d+)+)?/(segment(?:/\d+)+)?', 'gps.views.trace_tabs_html'),
                       #blocks html (nav ... )
                       (r'^nav.html', 'gps.views.nav_html'),
                       (r'^nearby.html', 'gps.views.nearby'),
                       #edit tracks
                       (r'^edit/(\d+)', 'gps.views.edit'),
                       #upload files
                       (r'^upload/$', 'gps.views.upload'),
                       (r'^modify/$', 'gps.views.modify'),
                       #login logout register
                       (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'gps/login.html'}),
                       (r'^logout/$', 'gps.views.logout'),
                       (r'^login/$', 'gps.views.login'),
                       (r'^register/$', 'gps.views.register'),
                       #JSON urls (usuall called with track number ?t=N)
                       (r'^trace/json$', 'gps.views.trace_json'),
                       (r'^trace/json_info$', 'gps.views.trace_json_info'),
                       (r'^trace/json_index$', 'gps.views.trace_json_index'),
                       #JSON urls (called with track number ?t=N&t2=...)
                       (r'^trace/json_segments$', 'gps.views.trace_segment_json'),
                       #Javascript
                       (r'^js/trace_(?P<maptype>ol|ign)_(?P<num>\d+).js', 'gps.views.view_trace_js'),

                       #ajax cookies
                       (r'^setmaptype/(?P<maptype>ol|ign)', 'gps.views.set_maptype'),

                       #tests
                       (r'^test_cookies', 'gps.views.test_cookies'),
                       (r'^test_ign', 'gps.views.test_ign'),
)
