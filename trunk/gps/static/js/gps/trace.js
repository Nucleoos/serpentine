var bounds, trackinfo, track_id, geographic;

function initEventsControls() {
$("#postchanges").click(function(e){
      e.preventDefault(); 
      var points = mainmap.layers[3].features[0].geometry.getVertices();
      var track_points = [];
      var elevation=0;
      for (var i in points) {
	  point = points[i].transform(map.getProjectionObject(),geographic);
	  elevation = getGroundElevation(point);
	  track_points.push({lon : point.x, lat:point.y, ele:elevation });
      }
      var json_string = JSON.stringify(track_points);
      $.post("/modify/",{"track":json_string} );
    });
$(".getElevation").click(function(e){
      e.preventDefault(); 
      alert("getElevation... coming soon");
    });
}

function initMainVariables() {
    $.jqplot.config.enablePlugins = true;
    //$.jqplot.eventListenerHooks.push(['jqplotMouseMove', showMarker]);
    //$.jqplot.eventListenerHooks.push(['jqplotZoom', handleZoom]);
        //$.jqplot.eventListenerHooks.push(['jqplotDblClick', plotTrace]);
    $.jqplot.postDrawHooks.push(drawSelection);
    trackinfo = getTrackInfos(track_id);//"{{ num }}"); //TODO unset track  ?
    bounds = new OpenLayers.Bounds(trackinfo["minlon"],trackinfo["minlat"],trackinfo["maxlon"],trackinfo["maxlat"]);
    initEventsControls();
}

$(document).ready(function() {  
    initMainVariables();
    resizeMap();
    setMainMap('ol',bounds,['terrain','hybrid']);
    initAfterMapSet();
});


//fonction appelée après setMap pour affichage traces etc.
function initAfterMapSet() {
    vec_pt = new OpenLayers.Layer.Vector("marqueur_pt");	    
    mainmap.addLayer(vec_pt);   
    //writeInfo(trackinfo);
    //addSnappingControls(map);
    track = getTrackPoints(track_id);
    plotTrace(track,"dist","ele");
    drawTrack(mainmap,track_id ,track, '#0000FF');
    resizeMap();
    var center = mainmap.getCenter();
    var cnt = center.transform(mainmap.getProjection(),geographic); 
    getTracksNearby( track_id , cnt.lat, cnt.lon);
    //Auto refresh mode

    mainmap.events.on({ "moveend": function (e) {
	getTracksNearby(track_id);
    }});

}

