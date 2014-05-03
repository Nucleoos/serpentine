// ------------------------------------------------------------
// fonctions pour appel track ajax -- renvoient des objets JSON
// ------------------------------------------------------------ 

function getTrackPoints(tr) {
    //renvoie l'ensemble des infos + points d'une trace
    var points;
    $.ajax({
	    url: "/trace/json",
	    datatype: 'json', 
	    data: ({t:tr}),
	    async: false,
	    success: function(data) {
		points = JSON.parse(data);		
	    }});
    return points;
}


function getMatchingPoints(t1,t2) {
    //renvoie l'ensemble des infos + points matchant deux traces
    var points;
    $('#seg_'+t2).html('searching...');
    $.ajax({
	    url: "/trace/json_segments",
	    datatype: 'json',
	    data: ({t1:t1,t2:t2}),
	    async: true,
	    success: function(data) {
		    points = JSON.parse(data);
		    if (points.length == 0) {
		        $('#seg_'+t2).html('No matches found');
		    }
		    else {
                $('#seg_'+t2).html('matches found');
                for (var i in points) {
                    drawTrack(mainmap,t2, points[i],'#FF0000', true, 8);
                }
	        }
	    },
	    error: function(XMLHttpRequest, textStatus, errorThrown) {
              alert("Status: " + textStatus); alert("Error: " + errorThrown);
           }
	    });
    return points;
}


function getTrackInfos(tr) {
    // renvoie les infos de base d'un track particulier
    var infos;
    $.ajax({
	    url: "/trace/json_info",
	    datatype: 'json', 
	    data: ({t:tr}),
	    async: false,
	    success: function(data) {
		infos = JSON.parse(data);		
	    }});
    return infos;
}
function getTrackIndex() {
    // renvoie une liste de tracks avec les infos pour affichage dans l'index
    var index;
    $.ajax({
	    url: "/trace/json_index",
	    datatype: 'json', 
	    async: false,
	    success: function(data) {
		index = JSON.parse(data);		
	    }});
    return index;
}

function getGroundElevation(point) {
    // renvoie les altitudes du tableau de points
    var elevation;
    $.ajax({
	    url: "http://api.geonames.org/gtopo30",
	    datatype: 'text',
	    data: ({lat:point.y, lng: point.x, username: "bdamay"}),
	    async: false,
	    success: function(data) {
		elevation = data;		
	    }});
    elevation = elevation.replace("\n","").replace("\r","");
    return elevation;
}

// Texte html
function getTracksFromBounds(bnds) {
    //recup du html nav et affectation aux div class nav
    $.ajax({
	    url: "/nav.html",
	    datatype: 'text', 
		data: ({minlat: bnds.bottom, minlon: bnds.left,
                        maxlat: bnds.top, maxlon: bnds.right}), 
	    async: true,
	    success: function(data) {
		$(".nav1").html(data);
	    }});
}

function getTracksNearby(tr_id, lat,lon) {
    //recup du html de la vue nearby et affectation à id=nearby_content
    $("#nearby_content").show(0);
    $("#nearby_content").html('<div class="ajaxgif"><img src="/static/img/ajax-loader.gif"/></div>');
    $.ajax({
	    url: "/nearby.html",
	    datatype: 'text', 
		data: ({tr_id: tr_id, lat: lat, lon: lon}),
	    async: true,
	    success: function(data) {
		$("#nearby_content").html(data);
	    }});
}

function getTrackInfoHtml(tr,div) {
    // renvoie le html du template info
    var infos;
    $.ajax({
	    url: "traceshortinfo/"+tr.toString(),
	    datatype: 'text', 
	    async: true,
	    success: function(data) {
		div.contentHTML = data;
		//$(".trackinfo").html = data;
		//div.autoSize = true;
		mainmap.addPopup(div);
	    }});
}