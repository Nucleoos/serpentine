function resizeMap(track) {
    $("#main_content").width($("#content").width()-$("#sidebar").width()-16);
    $("#map_canvas").width($("#main_content").width());
    $("#map_canvas").height($(window).height()-$("#header").height() -$("#charts").height()-5);
    $("#charts").width($("#main_content").width());
    $("#chartdiv").width($("#main_content").width());
    if (track != null) {
        plotTrace(track,"dist","ele");
    }
}

$(document).ready(function() {
    $("#toggle_plot_data").click(function(e){
        e.preventDefault();
        var toggle_html =$("#toggle_plot_data").html();
        if ( toggle_html == "afficher la vitesse"){
            plotTrace(track,"dist","speed");
            $("#toggle_plot_data").html("afficher l'altitude");
        }
        else {
            plotTrace(track,"dist","ele");
            $("#toggle_plot_data").html("afficher la vitesse");
        }
    });

    $("#logout").click(function(e){
        e.preventDefault();
        $.get("/logout");
        $("#login").html("formulaire");
    });

    $(".hideshow").click(
        function(e){
            if ($(this).next().css("display")=="none") {
                $(this).next().show(0); $(this).next().width(360)} //TODO: getPrevious witdh fo element
            else {$(this).next().hide(0); $(this).next().width(0)};
            resizeMap(track);

        }

    );

    $("#login_submit").click(function(e){
        e.preventDefault();
        $.post("/login/",{username:$("#id_username").val(),password:$("#id_password").val()});
    });

    $("#map_osm").click(function(e){
        e.preventDefault();
        alert('choix osm par défaut, recharger la page pour appliquer tout de suite');
        $.get("/setmaptype/ol",{});
    });

    $("#map_ign").click(function(e){
        e.preventDefault();
        alert('choix ign par défaut, recharger la page pour appliquer tout de suite');
        $.get("/setmaptype/ign",{});
    });

    $(".chart_action").click(function(e){
        e.preventDefault();
    });


    $(window).resize(function() {
        resizeMap(track);
    });
    resizeMap();
});
