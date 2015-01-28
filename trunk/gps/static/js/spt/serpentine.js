/* main js for serpentine */
$(document).ready(function() {
    //un track est défini
    SPT = Ui({
        mainmap_div: 'map_canvas',
        maintrack: ((typeof track_id !== 'undefined')? track_id : null)
    });
    SPT.initialise();
    // alert(SPT);
});

/**
 *  TRACK UI object
 *  */
var Ui = function(spec,my) {
    var that = {};
    that.width = $(document).width();
    that.height = $(document).height();
    if (spec.maintrack !== null){
        that.maintrack = Track({id:spec.maintrack});
    }
    /***
     * Initialise UI - bind main events etc.
     *
     * */
    that.initialise = function() {
        // event on click hideshow class
        // hides or show the next div
        $(".hideshow").click(
            function(e){
                if ($(this).next().css("display")=="none") {
                    $(this).next().show(0); $(this).next().width($(this).width())}
                else {$(this).next().hide(0); $(this).next().width(0)};
            }
        );
        this.resize();
        this.mainmap = Map({id:1, map_div: spec.mainmap_div, type: 'ol'});
        this.mainmap.zoomToExtent(bounds,true);
    }

    that.resize = function()  {
        $("#main_content").width($("#content").width()-$("#sidebar").width());
        $("#map_canvas").width($("#main_content").width());
        $("#map_canvas").height($(window).height()-$("#header").height() -$("#charts").height() -$(".user_message").outerHeight(true));
        $("#charts").width($("#main_content").width());
        $("#chartdiv").width($("#main_content").width());
        if (typeof this.mainmap != 'undefined') { this.mainmap.updateSize(); }
    }

    that.toString = function() {
        return "UI - "+this.mainmap_div + ' height:'+ this.height;

    }
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

var Map = function(spec,my) {
    cartographic = new OpenLayers.Projection("EPSG:900913");
    geographic = new OpenLayers.Projection("EPSG:4326");
    bounds =  new OpenLayers.Bounds(-2,42,4,51).transform(geographic, cartographic);

    var options = {
	    projection: cartographic,
	    displayProjection: geographic,
	    units: "m"
    };
    var map = new OpenLayers.Map(spec.map_div,options);
    //map.cartographic = cartographic;
    //map.geographic = geographic;
    var mapnik = new OpenLayers.Layer.OSM("osm mapnik");
    map.addLayer(mapnik);
    return map;
}
