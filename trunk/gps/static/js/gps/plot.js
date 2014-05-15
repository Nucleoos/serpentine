function plotTrace(track,abs,ord) {
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


//----------------------------------------------------

function plotSpeed2(track) {
    var spd = [];
    for (i in track.points) {
	spd.push([track.points[i]["time"], track.points[i]["speed"]]);
    }

    options =    {  show: true,
		    seriesColors: ["#444444"],
		    axes:{
	    xaxis:{renderer:$.jqplot.DateAxisRenderer, tickOptions:{fontSize:'7pt', formatString:'%H:%M'}},
	    yaxis:{tickOptions:{fontSize:'7pt',formatString:'%.1f'}, min:0 ,autoscale: true},
	    //xaxis:{tickOptions:{fontSize:'7pt'}, autoscale: true, min:0,  autoscale:true}
	},
		    series:[{label: 'speed', lineWidth: 1 , showMarker:false, neighborThreshold: -1}],
		    highlighter: {show: false},
		    legend: {location:'nw'},
		    cursor: {zoom: true, showTooltip:true, style: 'default', 
			     showVerticalLine:true,
			     showHorizontalLine:false,
			     showCursorLegend:true,
			     cursorLegendFormatString:'%s%s-%s'
		    }       
		   			  
    };
    plot1 = $.jqplot('speedchartdiv',  [spd],options);	
    plot1.replot(options);
}
