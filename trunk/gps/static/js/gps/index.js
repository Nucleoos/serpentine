$(document).ready(
    function() {  
	var trackindex = getTrackIndex(); // cherche en ajax la liste des traces à afficher
	var bounds = new OpenLayers.Bounds(trackindex["minlon"],trackindex["minlat"],trackindex["maxlon"],trackindex["maxlat"]);
	
	setMainMap('ol',bounds);
	var tracks = [];
	for (var i in trackindex){
	    tracks.push(trackindex[i]);
	}
	addMarkerTracks(mainmap,tracks);
	
	mainmap.events.on({ "moveend": function (e) {
	    var bnds =  mainmap.getExtent().transform(mainmap.getProjectionObject(), geographic);
	var cnt = mainmap.getCenter().transform(mainmap.getProjectionObject(),geographic);
	    getTracksFromBounds(bnds);
	    getTracksNearby(0,cnt.lat,cnt.lon);
	    // var maxbnds = mainmap.getMaxExtent().transform(mainmap.getProjectionObject(), geographic);
	}
});



   mainmap.zoomToExtent(bounds.transform(geographic, mainmap.getProjectionObject()));
    var cnt = mainmap.getCenter().transform(mainmap.getProjectionObject(),geographic);
   getTracksNearby(0,cnt.lat,cnt.lon);

   // afficher directement une nouvelle trace dans la carte en cours

 });
