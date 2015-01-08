function resizeMap() {
    $("#main_content").width($("#content").width()-$("#sidebar").width()-20);
    $("#map_canvas").width($("#main_content").width());
    $("#map_canvas").height($(window).height()-$("#header").height() -$("#charts").height()-5);
    $("#charts").width($("#main_content").width());
    $("#chartdiv").width($("#main_content").width());
    if (typeof plot1 != 'undefined') { plot1.replot(); }
    if (typeof mainmap != 'undefined') { mainmap.updateSize(); }
}

$(document).ready(function() {

    $(".hideshow").click(
        function(e){
            if ($(this).next().css("display")=="none") {
                $(this).next().show(0); $(this).next().width(360)} //TODO: getPrevious witdh fo element
            else {$(this).next().hide(0); $(this).next().width(0)};
            resizeMap();
        }
    );


    $(window).resize(function() {
        resizeMap();
    });
        resizeMap();
});
