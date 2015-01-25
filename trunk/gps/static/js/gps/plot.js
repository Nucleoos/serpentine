function plotTrace(track) {
    var series = getSeries(0,track.points.length);
    if (track.total_distance > 10) { fmt = '%.0f'; } else { fmt = '%.0f';}
    var options = { show: false, //true,
        seriesColors: ["#FF0000","#00AAAA"],
        seriesDefaults: {showMarker:false},
        series:[
            {label:'altitude',lineWidth: 2 , showMarker:false, neighborThreshold: -1},
            {yaxis:'y2axis',label:'vitesse',lineWidth: 2 , showMarker:false, neighborThreshold: -1}
        ],
        axes:{
            yaxis:{tickOptions:{showGridline: false,showMark: false, showLabel: true,shadow: false,fontSize:'7pt',formatString:'%.0f'}, autoscale: true},
            y2axis:{tickOptions:{showGridline: true,showMark: false, showLabel: true,shadow: false,fontSize:'7pt',formatString:'%.0f'}, min:0},
            xaxis:{tickOptions:{showGridline: true,showMark: false, showLabel: true,shadow: false,fontSize:'7pt',formatString:fmt},  min:0,  max:track.total_distance},
          },
        highlighter: {show: false}, //false},
        legend: {location:'nw'},
        cursor: {zoom: true, showTooltip:false, style: 'default',
            showVerticalLine:true,
            showCursorLegend:true,
            cursorLegendFormatString:'%s',
            constrainZoomTo: 'x'
        }
    };
    plot1 = $.jqplot('chartdiv',series,options);
    plot1.target.bind('jqplotZoom',handlePlotZoom);
    plot1.target.bind('jqplotMouseMove',showMarker);
    plot1.target.bind('mousewheel',mousewheel);
    plot1.replot(options);
    return plot1;
}

function mousewheel(ev) {
    ev.preventDefault();
   // alert('wheel '+ ev.originalEvent.wheelDelta);
   if (ev.originalEvent.wheelDelta<0) {
        var amp =  plot1.axes.xaxis.max -  plot1.axes.xaxis.min;
        var min =  plot1.axes.xaxis.min - amp/2 ;
        var max =  plot1.axes.xaxis.max + amp /2;
        if (min <0) {min = 0;}
        if (max > track.total_distance) {max = track.total_distance;}

        var series = getSeries(parseInt(getIndex(track, min)),parseInt(getIndex(track, max)));
        plot1.series[0].data  = series[0];
        plot1.series[1].data  = series[1];
        plot1.axes.xaxis.min = min;
        plot1.axes.xaxis.max = max;
        plot1.replot();
    }
}

function handlePlotZoom(ev, gridpos, datapos, plot, cursor) {
    var idxmin = parseInt(getIndex(track, plot.axes.xaxis.min));
    var idxmax = parseInt(getIndex(track, plot.axes.xaxis.max));
    series = getSeries(idxmin,idxmax);
    plot.series[0].data  = series[0];
    plot.series[1].data  = series[1];
    plot.replot();
/*
    if (idxmin == 0 && idxmax == track.point.length) {
        drawTrack(mainmap);
    } else {
        drawTrackPart(mainmap,"Zoom",track,idxmin,idxmax);
    }
    getTrackSegmentTables(track_id,idxmin,idxmax)
*/
}

function plotZoom(idxmin,idxmax) {
    var series = getSeries(idxmin,idxmax);
    plot1.series[0].data  = series[0];
    plot1.series[1].data  = series[1];
    plot1.axes.xaxis.min = track.points[idxmin].dist;
    plot1.axes.xaxis.max=track.points[idxmax].dist;
    plot1.replot();
}

function getSeries(idxmin, idxmax){
    var chartwidth = $('#chartdiv').width();
    var step = 1+Math.floor((idxmax-idxmin)/chartwidth);
    var speed = [];
    var ele =[];
    for (var i= idxmin; i< idxmax-step;i+=step) {
        var el = track.points[i]["ele"]
        var sp = track.points[i]["speed"]
        for(var j =1; j<step;j++) {el+=track.points[i+j]["ele"]; sp+=track.points[i+j]["speed"];}
        el = el/step; sp = sp/step;
        ele.push([track.points[i]["dist"],el]);
        speed.push([track.points[i]["dist"],sp]);
    }
    return [ele,speed]

}

function getRoundedTicks(minValue, maxValue, nbTicks) {
    //returns the rounded ticks for the axe
    //déterminer le pas yaxis
    var pas = 1; var ret = [];
    if ((maxValue-minValue)/nbTicks > 500) { pas = 500; }
    else if ((maxValue-minValue)/nbTicks > 100) {pas = 100 ; }
    else if ((maxValue-minValue)/nbTicks > 50) {pas = 50 ; }
    else if ((maxValue-minValue)/nbTicks > 10) {pas = 20 ; }
    else if ((maxValue-minValue)/nbTicks > 10) {pas = 10 ; }
    else if ((maxValue-minValue)/nbTicks > nbTicks) {pas = 5 ; }
    else if ((maxValue-minValue)/nbTicks > 2) {pas = 2 ; }
    else if ((maxValue-minValue)/nbTicks > 1) {pas = 1 ; }
    else if ((maxValue-minValue)/nbTicks > 0.5) {pas = 0.5 ; }
    minValue = (parseInt(minValue/pas))*pas;
    for (i=minValue;i<maxValue+pas;i+=pas) {
        ret.push(i);
    }
    return ret;
}


