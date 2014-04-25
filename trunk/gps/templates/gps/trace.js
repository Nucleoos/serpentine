var  mainmap, bounds, trackinfo, track_id, geographic;

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
    $.jqplot.eventListenerHooks.push(['jqplotMouseMove', showMarker]);
    $.jqplot.postDrawHooks.push(showAlert);
    track_id = "{{ num }}";
    trackinfo = getTrackInfos(track_id);//"{{ num }}"); //TODO tracker l'exception du track inexistant
    bounds = new OpenLayers.Bounds(trackinfo["minlon"],trackinfo["minlat"],trackinfo["maxlon"],trackinfo["maxlat"]);
    initEventsControls();
}

$(document).ready(function() {  
    initMainVariables();
    resizeMap();
    setMainMap('{{ maptype }}',bounds);
    if ('{{ maptype }}'=='ol') { initAfterMapSet();}
});


//fonction appelée après setMap pour affichage traces etc.
function initAfterMapSet() {
    vec_pt = new OpenLayers.Layer.Vector("marqueur_pt");	    
    mainmap.addLayer(vec_pt);   
    //writeInfo(trackinfo);
    //addSnappingControls(map);
    track = getTrackPoints("{{ num }}");
    drawTrack(mainmap,"{{ num }}" ,track);
    if ("{{ fullscreen }}" == "fullscreen"){
       fullscreen = true;
    }
//    addPanelControls(mainmap,"track");
    resizeMap();
    var center = mainmap.getCenter();
    var cnt = center.transform(mainmap.getProjection(),geographic); 
    getTracksNearby(cnt.lat,cnt.lon);   
    mainmap.events.on({ "moveend": function (e) {
	var cnt = mainmap.getCenter().transform(mainmap.getProjectionObject(),geographic);
	getTracksNearby(cnt.lat,cnt.lon);   
    }
		      });
    
}



   // afficher directement une nouvelle trace dans la carte en cours
   /*
     $(".a_track").click(function(evt){
	   evt.preventDefault();
	   rg = new RegExp("^trace_([0-9]*)");
	   tr = rg.exec(this.id);
	   track=getTrack(tr[1]);
	   //	   Tracks.push(track);
	   drawTrack(map,tr[1], track);
       });
   */