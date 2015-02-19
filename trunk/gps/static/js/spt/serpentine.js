/* main js for serpentine */
$(document).ready(function() {
    //check du page_ui passé par la page
    if (typeof sptui !== 'object') {
        sptui = {type: 'base'}
    }
    SPT = Ui(sptui);
    SPT.initialise();
    // alert(SPT);
});

/**
 * UI object
 *  */
var Ui = function(spec,my) {
    /** attributs **/
    var that = {};
    that.type = (spec.hasOwnProperty('type') ? spec.type : 'base');
    that.track_id = (spec.hasOwnProperty('track_id') ? spec.track_id : -1);
    that.width = $(document).width();
    that.height = $(document).height();
    if (spec.hasOwnProperty('track_id')){
        that.track = Track({id:that.track_id});
    }
    /**  Méthodes */

    //initialise ui
    that.initialise = function() {
        // event on click hideshow class // hides or show the next div
        $(".hideshow").on('click',
            function(e){
                if ($(this).next().css("display")=="none") {
                    $(this).next().show(0); $(this).next().width($(this).width())}
                else {$(this).next().hide(0); $(this).next().width(0)};
            }
        );
        $("#header").on("dblclick", function() {that.resizeUi()});
        $(window).resize(function() {
            that.resizeUi();
        });
        this.resizeUi();

        // Map init stuff
        if (this.type === 'track') {
            this.mainmap = SerpentineMap({id:1, map_div: spec.mainmap_div, type: 'ol'},{});
            this.mainmap.initialise();
            this.plot = Plot({id:1});
            this.plot.initialise();
        }
        // Track stuff
        if (this.track !== undefined && this.type === 'track') {
            this.mainmap.drawTrack(this.mainmap, this.track);
        }

    }

    // auto resize
    that.resizeUi = function()  {
        if ($("#header").outerWidth()*0.3 > 300) {
        $("#sidebar").outerWidth($("#header").outerWidth()*0.35);
        } else {$("#sidebar").outerWidth(300);}
        $("#main_content").outerWidth($("#content").outerWidth(true)-$("#sidebar").outerWidth(true)-1);

        $("#map_canvas").outerWidth($("#main_content").outerWidth())
        $("#charts").outerWidth($("#map_canvas").outerWidth());
        $("#map_canvas").outerHeight($(window).height()-$("#header").outerHeight(true) -$("#charts").outerHeight(true) -$(".user_message").outerHeight(true));

        if (typeof this.mainmap != 'undefined') { this.mainmap.updateSize(); }
        console.log('resizeUI');
    }

    that.toString = function() {
        return "UI - "+this.mainmap_div + ' height:'+ this.height;

    }

    that.addTrack = function(id) {
       var track=Track({id:id});

       drawTrack(this.mainmap, track,{style:{strokeWidth:3, strokeColor:'#333333'}});
    }

    //return instance of that
    return that;
}

/**
 * track object
 */
// constructor
var Track = function(spec,my) {
    var that = {}; // the object to be returned
    my = my || {}
    that.id = spec.id;
    if (spec.id !==0) {
        var json = function() {
            var ajax = $.ajax({
                url: "/trace/json",
                datatype: 'json',
                data: ({t:that.id}),
                async: false,
                success: function(data) {
                }});
            return JSON.parse(ajax.responseText);
        }();
        that.points = json.points;
        that.total_time = json.total_time;
    }
    that.toString = function(){
        return 'track '+ that.id ;
    };

    return that;
}

var SerpentineMap = function(spec,my) {
    var that = {};
    if (spec.type === "ign") {
        //chargement ign avec viewer getMap()
    } else {
        that = new OpenLayers.Map(spec.map_div);
    }
    that.cartographic = new OpenLayers.Projection("EPSG:900913");
    that.geographic = new OpenLayers.Projection("EPSG:4326");
    that.options = {
	    projection: that.cartographic,
	    displayProjection: that.geographic,
	    units: "m"
    };

    that.initialise = function() {
        this.addLayer(new OpenLayers.Layer.OSM("osm mapnik"));
        var bounds =  new OpenLayers.Bounds(-2,42,4,51).transform(this.geographic, this.cartographic);
        this.zoomToExtent(bounds,true);
    }

    that.drawTrack = function(map, track, options) {
        options = (options ===  undefined) ? {} : options;
        if (track.vector != undefined) {
              map.removeLayer(track.vector);
        }
        track.vector = new OpenLayers.Layer.Vector(track.name);
        var idxmin =  (options.hasOwnProperty('idxmin')) ? options.idxmin : 0;
        var idxmax =  (options.hasOwnProperty('idxmax')) ? options.idxmax : 9999999999999;
        var zoom =  (options.hasOwnProperty('zoom')) ? options.zoom : true; // par défaut on zoome sur la ligne

        var track_points = [];
        for (i in track.points) {
            if (parseInt(i) >= parseInt(idxmin) && parseInt(i) < parseInt(idxmax)) {
                var point = new OpenLayers.Geometry.Point(track.points[i]["lon"],  track.points[i]["lat"]);
                track_points.push(point.transform(map.geographic,map.getProjectionObject()));
            }
        }
        var line_style = (options.hasOwnProperty('style')) ? option.style : { strokeWidth: 3, strokeColor: 'blue', strokeOpacity: 0.7 };
        var lineGeometry =   new OpenLayers.Geometry.LineString(track_points);
        var lineFeature = new OpenLayers.Feature.Vector(lineGeometry,null,line_style);
        track.vector.addFeatures(lineFeature);
        map.addLayer(track.vector);
        if (zoom) {
            map.zoomToExtent(lineGeometry.getBounds());
        }
        return lineGeometry;
    }

    return that;
}

/***************
 * plot object *
 ***************/
// constructor
var Plot = function(spec,my) {
    var that =  $.jqplot('chartdiv',[[1,2,3,2,6]]); // Plot is a jqPlot object
    my = my || {}
    that.id = spec.id;
    that.initialise = function() {
        return this;
    }
    that.toString = function(){
        return 'plot '+ that.id ;
    };
    return that;
}
