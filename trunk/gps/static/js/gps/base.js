var fullscreen = false;

function resizeMap() {
    if (!fullscreen) {
	$("#map_canvas").width($("#content").width()-$("#sidebar").width()-20);
	$("#map_canvas").height($(window).height()-$("#header").height()-30 -$("#text_content").height());
    }
    else {
	$("#map_canvas").addClass("absolute");
	$("#map_canvas").width($(window).width());
	$("#map_canvas").height($(window).height());
    }
    $("#main_content").width($("#content").width()-$("#sidebar").width()-18);
}

$(document).ready(function() {
	$("#fullscreen").click(function(e){
		e.preventDefault(); 
		fullscreen = true;
		resizeMap();
	    });
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
	$(".sidetitle").click(
			      function(e){
				  if ($(this).next().css("display")=="none") {
				      $(this).next().show(0)}
				  else {$(this).next().hide(0)};
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

	$(window).resize(function() {
		resizeMap();
	    });
	resizeMap();
    });
