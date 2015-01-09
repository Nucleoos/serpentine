/* main js for serpentine */
$(document).ready(function() {
   SPT = ui({
       map_canvas: 'map_canvas',
       track:track({id:track_id})
   });
   alert('Track =  ' + SPT.track.toString() );
});

/**
 *  UI object
 *  */
var ui = function(spec,my) {
    var that = {};
    that.map_canvas = spec.map_canvas || '';
    that.width = $(document).width();
    that.height = $(document).height();
    that.track = spec.track;
    that.initialise = function() {
        alert(that.height + ' '+that.map_canvas);
    }
    return that;
}

/**
 * track object
 */
// constructor
var track = function(spec,my) {
    var that = {}; // the object to be returned
    my = my || {}
    that.id = spec.id;
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
    that.toString = function(){
       return 'track '+ that.id ;
    };

    return that;
}

