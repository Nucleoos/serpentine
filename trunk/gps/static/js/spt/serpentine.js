/* main js for serpentine */
$(document).ready(function() {
    //un track est défini
    var SPT = ui({
        mainmap_div: 'map_canvas',
        maintrack: ((typeof track_id !== 'undefined')? track_id : null)
    });
    SPT.initialise();
    // alert(SPT);
});

/**
 *  TRACK UI object
 *  */
var ui = function(spec,my) {
    var that = {};
    that.mainmap_div = spec.mainmap_div;
    that.width = $(document).width();
    that.height = $(document).height();
    if (spec.maintrack !== null){
        that.maintrack = track({id:spec.maintrack});
    }
    /***
     * Initialise UI - bind main events etc.
     */
    that.initialise = function() {
        // event on click hideshow class
        // hides or show the next div
        $(".hideshow").click(
            function(e){
                if ($(this).next().css("display")=="none") {
                    $(this).next().show(0); $(this).next().width($(this).width())} //TODO: getPrevious witdh fo element
                else {$(this).next().hide(0); $(this).next().width(0)};
                resizeMap();
            }
        );
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
var track = function(spec,my) {
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

