var  mainmap, geographic, selectControl, clickControl , vec_track, vec_t, viewer,iv; 

function setMainMap(type,bounds) {
    geographic = new OpenLayers.Projection("EPSG:4326"); //projection lat lon
    if (type=='ign') {
	setIgnMap(bounds);
    } 
    else {
	setOsmMap(bounds);
    }
}

function setIgnMap(bounds) {
    function initIgnMap() {
	viewer = iv.getViewer();
	iv.setLayerOpacity('GEOGRAPHICALGRIDSYSTEMS.MAPS',0.8);
	mainmap = viewer.getMap();
	mainmap.zoomToExtent(bounds.transform(OpenLayers.Projection.CRS84, mainmap.getProjection()),true);
	initAfterMapSet();
    }
    iv = Geoportal.load('map_canvas', '4440190236596604228',
			null, //center
			null, //zoom
			{   
			    layers:['GEOGRAPHICALGRIDSYSTEMS.MAPS'],
			    mode: 'normal',
			    onView : initIgnMap,
			} //options
		       );
    
}

function setOsmMap(bounds) {
    var map;
    var cartographic = new OpenLayers.Projection("EPSG:900913");	
    var options = {
	projection: cartographic,
	displayProjection: geographic,
	units: "m",
    };   
    map = new OpenLayers.Map("map_canvas",options); 
    map.addControl(new OpenLayers.Control.LayerSwitcher());
    var mousePosCtl = new OpenLayers.Control.MousePosition({displayProjection: geographic});
    map.addControl(mousePosCtl);
    
    var mapnik = new OpenLayers.Layer.OSM("osm mapnik");
    var hybrid = new OpenLayers.Layer.Google(
					     "hybrid google maps", {type:  google.maps.MapTypeId.HYBRID,'sphericalMercator': true,
								    numZoomLevels: 20} );
    map.addLayer(mapnik);
    map.addLayer(hybrid);
    mainmap = map;       
}

function addPanelControls(map,trackname){
    var panel = new OpenLayers.Control.Panel({displayClass: "olControlEditingToolbar" });
    var modifyControl = new OpenLayers.Control.ModifyFeature(
							     map.getLayersByName(trackname)[0], 
							     {displayClass: "olControlModifyFeature", title: "Modify Features"});            


    var lineControl= new OpenLayers.Control.DrawFeature(map.getLayersByName(trackname)[0], OpenLayers.Handler.Path);
    panel.addControls([new OpenLayers.Control.Navigation({title: "Navigate"}),lineControl, modifyControl]);
    map.addControl(panel);
    map.addControl(modifyControl);
}

function modifyTrack(map,track){
    // duplique la trace passée en paramètre et positionne les modify features dessus    
}

function drawTrack(map, trackname, track,color, adding, width) {
    width = typeof width !== 'undefined' ? width : 3;
    vec_track = new OpenLayers.Layer.Vector("track");
    var track_points = [];
    for (i in track.points) {
	var point = new OpenLayers.Geometry.Point(track.points[i]["lon"],  track.points[i]["lat"]);
	track_points.push(point.transform(geographic,map.getProjectionObject()));
    }
    var line_style = { strokeWidth: width, strokeColor: color, strokeOpacity: 0.7 };
    var lineGeometry =   new OpenLayers.Geometry.LineString(track_points);
    var lineFeature = new OpenLayers.Feature.Vector(lineGeometry,null,line_style);
    map.addLayer(vec_track);
    vec_track.addFeatures(lineFeature);
    if (!adding) {
        map.zoomToExtent(lineGeometry.getBounds());
        }
    return lineGeometry;
}

function getModifiedTrack(points){
    
    var track_points = [];
    for (i in points) {
	var point = points[i];
	track_points.push(point.transform(map.getProjectionObject(),geographic));
    }

}

function getIndex(track, distance) {
    for(var i in track.points) {
	if (track.points[i]["dist"] >= distance) return i;
    }
    return 0;
}

function showAlert() {
    //Vérifier s'il s'agit d'un zoom ou pas
    if (this.axes.xaxis.min > 0){ 
	var idxmin = getIndex(track, this.axes.xaxis.min);
	var idxmax = getIndex(track, this.axes.xaxis.max);	    
	//	alert("min" + this.axes.xaxis.min+ " idx "+idxmin + "/" +this.axes.xaxis.max + " idx "+idxmax);
	drawTrackPart(mainmap,"Zoom",track,idxmin,idxmax);
    }
}

function drawTrackPart(map, trackname, track, idxmin, idxmax) {
    if (vec_t != undefined) {
	map.removeLayer(vec_t);
    }
    vec_t = new OpenLayers.Layer.Vector("track_part");
    var track_points = [];
    for (i in track.points) {
	if (parseInt(i) >= parseInt(idxmin) && parseInt(i) < parseInt(idxmax)) {
	    var point = new OpenLayers.Geometry.Point(track.points[i]["lon"],  track.points[i]["lat"]);
	    track_points.push(point.transform(geographic,map.getProjectionObject()));
	}
    }
    var line_style = { strokeWidth: 5, strokeColor: '#FF0000', strokeOpacity: 0.7 };
    var lineGeometry =   new OpenLayers.Geometry.LineString(track_points);
    var lineFeature = new OpenLayers.Feature.Vector(lineGeometry,null,line_style);
    vec_t.addFeatures(lineFeature);
    map.addLayer(vec_t);
    var bnds = lineGeometry.getBounds();
    map.zoomToExtent(bnds);
    return lineGeometry;
}

function showMarker(e, gridpos, datapos, neighbor, plot) {    
    var vec_pt = mainmap.getLayersBy('name','marqueur_pt')[0];
    vec_pt.removeAllFeatures();
    var x = datapos.xaxis; // la position en km sur l'axe
    var i = getIndex(track,x); //recherche le point d'index du repère en km
    var marker_style = {
	externalGraphic: "/static/img/marker.png",
	'graphicHeight': 25,
	'graphicWidth': 25,
	'graphicXOffset': -12.5,
	'graphicYOffset': -25,      
	//	pointerEvents: "visiblePainted"
    };    
    var point = new OpenLayers.Geometry.Point(track.points[i]["lon"],  track.points[i]["lat"]);
    point = point.transform(geographic, mainmap.getProjectionObject());
    var pointFeature = new OpenLayers.Feature.Vector(point,null, marker_style);
    vec_pt.addFeatures(pointFeature);
    $("#order_num").html(i);
}

function addMarkerTracks(map, tracks) {
    //afficher sur une carte les markers d'un tableau de traces passées en paramètre 
    markers = new OpenLayers.Layer.Vector("markers");
    var marker_style = 
	{
	    'graphicHeight': 25,
	    'graphicWidth': 25,
	    'graphicXOffset': -12.5,
	    'graphicYOffset': -25,      
	    externalGraphic: "/static/img/marker.png",
	    cursor: 'pointer',
	    //      pointerEvents: "visiblePainted"
	};

    for(var i in tracks){
	var point = new OpenLayers.Geometry.Point(tracks[i]["lon"],  tracks[i]["lat"]).transform(geographic, map.getProjectionObject());
	var pointFeature = new OpenLayers.Feature.Vector(point,tracks[i], marker_style);
	markers.addFeatures(pointFeature);
    }

    //ajoute un listener sur chaque marqueur
     selectControl = new OpenLayers.Control.SelectFeature(markers, {
	     //hover: true,
	    highlightOnly: true, renderIntent: "temporary",
	    eventListeners: {
		featurehighlighted: onFeatureSelect,		
		//		featureunhighlighted: onFeatureUnselect,

	    }
	});
    
    selectControl.events.on({"featureselected":onFeatureSelect});
        map.addControl(selectControl);
    selectControl.activate();
    map.addLayer(markers);  
}
function onFeatureSelect(evt) {
    feature = evt.feature;   
    //    trackinfo = getTrackInfos(feature.attributes.id);
    popup = new OpenLayers.Popup.Anchored("track_popup",
					  feature.geometry.getBounds().getCenterLonLat(),
					  new OpenLayers.Size(180,30),
					  '<div class="ajaxgif"><img src="static/img/ajax-loader.gif"/></div>'
					  ,
					  null, true, onPopupClose);
    //    popup.autoSize = true;

    feature.popup = popup;
    popup.feature = feature;
   
    mainmap.addPopup(popup);	//alert('event');
    
    getTrackInfoHtml(feature.attributes.id,popup);	
    //	mainmap.addPopup(popup);	//alert('event');


    
}
function onFeatureClick(evt) {
    feature = evt.feature;   
    alert(feature.attributes.id);
 
}

function onPopupClose(evt) {
    //    selectControl.unselect(this.feature);
    this.feature = null;     
    mainmap.removePopup(this);
    this.destroy();
}

function onFeatureUnselect(evt) {
    feature = evt.feature;
    if (feature.popup) {
        popup.feature = null;
        mainmap.removePopup(feature.popup);
        feature.popup.destroy();
        feature.popup = null;
    }   
}

function getColor() {
    // mettre ici le code qui prend la couleur choisie dans une palette
    return '#0000FF';
}


function  addTrack(id) {
   var track=getTrackPoints(id);
   drawTrack(mainmap,id, track,'#333333', true);
}


//regexp example
//rg = new RegExp("^trace_([0-9]*)");
//tr = rg.exec(id);