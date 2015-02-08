(function(){
  //UI configuration
  var itemSize = 18,
    cellSize = itemSize-1,
    width = 1600,
    height = 800,
    margin = {top:20,right:20,bottom:20,left:25};

  //formats
  var hourFormat = d3.time.format('%H'),
    dayFormat = d3.time.format('%j'),
    timeFormat = d3.time.format('%Y-%m-%dT%X'),
    monthDayFormat = d3.time.format('%m.%d');

  //data vars for rendering
  var dateExtent = null,
    data = null,
    dayOffset = 0,
//    colorCalibration = ['#f6faaa','#FEE08B','#FDAE61','#F46D43','#D53E4F','#9E0142'],
    colorCalibration = ['#ffffff', '#e0e0e0', '#c0c0c0', '#a0a0a0', '#808080', '#606060', '#404040', '#202020', '#000000'],
    dailyValueExtent = {};

  //axises and scales
  var axisWidth = 0 ,
    axisHeight = itemSize*24,
    xAxisScale = d3.time.scale(),
    xAxis = d3.svg.axis()
      .orient('top')
      .ticks(d3.time.days,3)
      .tickFormat(monthDayFormat),
    yAxisScale = d3.scale.linear()
      .range([0,axisHeight])
      .domain([0,24]),
    yAxis = d3.svg.axis()
      .orient('left')
      .ticks(5)
      .tickFormat(d3.format('02d'))
      .scale(yAxisScale);

  initCalibration();

  var svg = d3.select('[role="heatmap"]');
  var heatmap = svg
    .attr('width',width)
    .attr('height',height)
  .append('g')
    .attr('width',width-margin.left-margin.right)
    .attr('height',height-margin.top-margin.bottom)
    .attr('transform','translate('+margin.left+','+margin.top+')');
  var rect = null;

  d3.json('/homecontroller/electricity/get_json', function(err,data){
//    data = data.data;
    data.forEach(function(valueObj){
      valueObj['date'] = timeFormat.parse(valueObj['timestamp']);
      var day = valueObj['day'] = monthDayFormat(valueObj['date']);

      var dayData = dailyValueExtent[day] = (dailyValueExtent[day] || [30,-1]);
      var pmValue = valueObj['value']['W'];
      dayData[0] = d3.min([dayData[0],pmValue]);
      dayData[1] = d3.max([dayData[1],pmValue]);
    });

    dateExtent = d3.extent(data,function(d){
      return d.date;
    });

    axisWidth = itemSize*(dayFormat(dateExtent[1])-dayFormat(dateExtent[0])+1);

    //render axises
    xAxis.scale(xAxisScale.range([0,axisWidth]).domain([dateExtent[0],dateExtent[1]]));
    svg.append('g')
      .attr('transform','translate('+margin.left+','+margin.top+')')
      .attr('class','x axis')
      .call(xAxis)
    .append('text')
      .text('date')
      .attr('transform','translate('+axisWidth+',-10)');

    svg.append('g')
      .attr('transform','translate('+margin.left+','+margin.top+')')
      .attr('class','y axis')
      .call(yAxis)
    .append('text')
      .text('time')
      .attr('transform','translate(-10,'+axisHeight+') rotate(-90)');

    //render heatmap rects
    dayOffset = dayFormat(dateExtent[0]);
    rect = heatmap.selectAll('rect')
      .data(data)
    .enter().append('rect')
      .attr('width',cellSize)
      .attr('height',cellSize)
      .attr('x',function(d){
        return itemSize*(dayFormat(d.date)-dayOffset);
      })
      .attr('y',function(d){
        return hourFormat(d.date)*itemSize;
      })
      .attr('fill','#ffffff');

    rect.filter(function(d){ return d.value['W']>0;})
      .append('title')
      .text(function(d){
        return monthDayFormat(d.date)+' '+d.value['W'];
      });

    renderColor();
  });

  function initCalibration(){
    d3.select('[role="calibration"] [role="example"]').select('svg')
      .selectAll('rect').data(colorCalibration).enter()
    .append('rect')
      .attr('width',cellSize)
      .attr('height',cellSize)
      .attr('x',function(d,i){
        return i*itemSize;
      })
      .attr('fill',function(d){
        return d;
      });

    //bind click event
    d3.selectAll('[role="calibration"] [name="displayType"]').on('click',function(){
      renderColor();
    });
  }

  function renderColor(){
    var renderByCount = document.getElementsByName('displayType')[0].checked;

    rect
      .filter(function(d){
        return (d.value['W']>=0);
      })
      .transition()
      .delay(function(d){
        return (dayFormat(d.date)-dayOffset)*15;
      })
      .duration(500)
      .attrTween('fill',function(d,i,a){
        //choose color dynamicly
        var colorIndex = d3.scale.quantize()
          .range([0,1,2,3,4,5,6,7,8])
          .domain((renderByCount?[0,1]:dailyValueExtent[d.day]));

        return d3.interpolate(a,colorCalibration[colorIndex(d.value['W'])]);
      });
  }

  //extend frame height in `http://bl.ocks.org/`
  d3.select(self.frameElement).style("height", "600px");
})();


var electricity_info;
$(document).ready(function () {

  $("#main-button-box .electricity").on("click", function() {
    switchVisibleContent("#electricity-modal");
  });
  $("#electricity-modal .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
