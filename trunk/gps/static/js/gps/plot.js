
function plotTraceOld(track,abs,ord) {
    var data = [];
    var ticksY= [];
    var maxOrd = 0; var minOrd= 100000;
    for (i in track.points) {
        data.push([track.points[i][abs],track.points[i][ord]]);
        if (track.points[i][ord] > maxOrd) {maxOrd = track.points[i][ord];}
        if (track.points[i][ord] < minOrd) {minOrd = track.points[i][ord];}
    }
    ticksY = getRoundedTicks(minOrd,maxOrd,5);
    if (track.total_distance > 1) { fmt = '%.0f'; } else { fmt = '%.1f';}
    options = { show: false, //true,
        seriesColors: ["#FF0000"],
        axes:{ yaxis:{tickOptions:{showGridline: false,showMark: false, showLabel: false,shadow: false,fontSize:'7pt',formatString:'%.0f'}, autoscale: true, ticks: ticksY},
            xaxis:{tickOptions:{showGridline: false,showMark: false, showLabel: false,shadow: false,fontSize:'7pt',formatString:fmt}, min:0,  max:track.total_distance}},
        series:[{label: ord, lineWidth: 1 , showMarker:false, neighborThreshold: -1}],
        highlighter: {show: true}, //false},
        legend: {location:'nw'},
        cursor: {zoom: true, showTooltip:false, style: 'default',
            showVerticalLine:true,
            showCursorLegend:true,
            cursorLegendFormatString:'%s | %s | %s',
            constrainZoomTo: 'x'
        }
    };
    plot1 = $.jqplot('chartdiv',[data],options);
    plot1.replot(options);
    return plot1;
}

function plotTrace2(track) {
    var speed = [];
    var ele =[];
    var speedi = [];
    var maxOrd = 0; var minOrd= 100000;
    for (i in track.points) {
        ele.push([track.points[i]["dist"],track.points[i]["ele"]]);
        speed.push([track.points[i]["dist"],track.points[i]["speed"]]);
    }
    if (track.total_distance > 1) { fmt = '%.0f'; } else { fmt = '%.0f';}
    options = { show: false, //true,
        seriesColors: ["#FF0000","#00AAAA"],
        seriesDefaults: {showMarker:false},
        series:[
            {label:'altitude',lineWidth: 2 , showMarker:false, neighborThreshold: -1},
            {yaxis:'y2axis',label:'vitesse',lineWidth: 2 , showMarker:false, neighborThreshold: -1}
        ],
        axes:{
            yaxis:{tickOptions:{showGridline: false,showMark: false, showLabel: false,shadow: false,fontSize:'7pt',formatString:'%.0f'}, autoscale: true},
            xaxis:{tickOptions:{showGridline: false,showMark: false, showLabel: false,shadow: false,fontSize:'7pt',formatString:fmt}, min:0,  max:track.total_distance},
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
    plot1 = $.jqplot('chartdiv',[ele,speed],options);
    plot1.replot(options);
    return plot1;
}

function plotTrace(track) {
    var series = getSeries(0,track.points.length);
    if (track.total_distance > 1) { fmt = '%.0f'; } else { fmt = '%.0f';}
    var options = { show: false, //true,
        seriesColors: ["#FF0000","#00AAAA"],
        seriesDefaults: {showMarker:false},
        series:[
            {label:'altitude',lineWidth: 2 , showMarker:false, neighborThreshold: -1},
            {yaxis:'y2axis',label:'vitesse',lineWidth: 2 , showMarker:false, neighborThreshold: -1}
        ],
        axes:{
            yaxis:{tickOptions:{showGridline: false,showMark: false, showLabel: true,shadow: false,fontSize:'7pt',formatString:'%.0f'}, autoscale: true},
            y2axis:{tickOptions:{showGridline: true,showMark: false, showLabel: true,shadow: false,fontSize:'7pt',formatString:'%.0f'}, autoscale: true},
            xaxis:{tickOptions:{showGridline: true,showMark: false, showLabel: true,shadow: false,fontSize:'7pt',formatString:'%.0f'}, min:0,  max:track.total_distance},
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
//    plot1.target.bind('mousewheel',mousewheel)
    plot1.replot(options);
    return plot1;
}

function mousewheel(ev) {
  /*  if (ev.originalEvent.wheelDelta<0) {
        var idxmin = parseInt(getIndex(track, plot1.axes.xaxis.min));
        var idxmax = parseInt(getIndex(track, plot1.axes.xaxis.max));
        series = getSeries(idxmin/2,idxmax);
        plot1.series[0].data  = series[0];
        plot1.series[1].data  = series[1];
        plot1.replot();
    }*/
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


