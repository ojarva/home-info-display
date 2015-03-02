var ElectricityInfo = function () {
  "use strict";
  function drawHeatmap() {
    //UI configuration
    var itemSize = 18,
        cellSize = itemSize - 1,
        width = 1600,
        height = 480,
        margin = {top: 20, right: 20, bottom: 20, left: 41};

    var dayFormat_orig = d3.time.format("%j");
    var yearFormat_orig = d3.time.format("%Y");

    function dayFormat(timestamp) {
      var val = 0 - (0 - dayFormat_orig(timestamp)) - (0 - yearFormat_orig(timestamp) * 365);
      return val;
    }

    var hourFormat = d3.time.format("%H"),
        timeFormat = d3.time.format("%Y-%m-%dT%X"),
        monthDayFormat = d3.time.format("%d.%m.");

    //data vars for rendering
    var dateExtent = null,
      data = null,
      dayOffset = 0,
      colorCalibration = ["#ffffff", "#e0e0e0", "#c0c0c0", "#a0a0a0", "#808080", "#606060", "#404040", "#202020", "#000000"],
      dailyValueExtent = {};

    //axes and scales
    var axisWidth = 0,
      axisHeight = itemSize * 24,
      xAxisScale = d3.time.scale(),
      xAxis = d3.svg.axis()
        .orient("top")
        .ticks(d3.time.days, 3)
        .tickFormat(monthDayFormat),
      yAxisScale = d3.scale.linear()
        .range([0, axisHeight])
        .domain([0, 24]),
      yAxis = d3.svg.axis()
        .orient("left")
        .ticks(5)
        .tickFormat(d3.format("02d"))
        .scale(yAxisScale);

    initCalibration();

    var svg = d3.select("[role='heatmap']"); // TODO: only select inside electricity modal
    var heatmap = svg
      .attr("width", width)
      .attr("height", height)
    .append("g")
      .attr("width", width-margin.left-margin.right)
      .attr("height", height-margin.top-margin.bottom)
      .attr("transform", "translate("+margin.left+","+margin.top+")");
    var rect = null;

    d3.json("/homecontroller/electricity/get_json", function(err, data){
      data.forEach(function(valueObj){
        valueObj["date"] = timeFormat.parse(valueObj["timestamp"]);
        var day = valueObj["day"] = monthDayFormat(valueObj["date"]);

        var dayData = dailyValueExtent[day] = (dailyValueExtent[day] || [30, -1]);
        var pmValue = valueObj["value"]["W"];
        dayData[0] = d3.min([dayData[0], pmValue]);
        dayData[1] = d3.max([dayData[1], pmValue]);
      });

      dateExtent = d3.extent(data, function(d){
        return d.date;
      });

      axisWidth = itemSize * (dayFormat(dateExtent[1]) - dayFormat(dateExtent[0]) + 1);

      //render axes
      xAxis.scale(xAxisScale.range([0, axisWidth]).domain([dateExtent[0], dateExtent[1]]));
      svg.append("g")
        .attr("transform", "translate("+margin.left+","+margin.top+")")
        .attr("class", "x axis")
        .call(xAxis)
      .append("text")
        .text("pvm")
        .attr("transform", "translate("+axisWidth+",-10)");

      svg.append("g")
        .attr("transform", "translate("+margin.left+","+margin.top+")")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .text("aika")
        .attr("transform", "translate(-10,"+axisHeight+") rotate(-90)");

      // render heatmap rects
      dayOffset = dayFormat(dateExtent[0]);
      rect = heatmap.selectAll("rect")
        .data(data)
      .enter().append("rect")
        .attr("width", cellSize)
        .attr("height", cellSize)
        .attr("x", function(d){
          return itemSize * (dayFormat(d.date) - dayOffset);
        })
        .attr("y", function(d){
          return hourFormat(d.date) * itemSize;
        })
        .attr("fill", "#ffffff");

      rect.filter(function(d){ return d.value["W"] > 0;})
        .append("title")
        .text(function(d) {
          return monthDayFormat(d.date) + " " + d.value["W"];
        });

      renderColor();
    });

    function initCalibration(){
      d3.select("[role='calibration'] [role='example']").select("svg")
        .selectAll("rect").data(colorCalibration).enter()
      .append("rect")
        .attr("width", cellSize)
        .attr("height", cellSize)
        .attr("x", function(d, i){
          return i * itemSize;
        })
        .attr("fill", function(d){
          return d;
        });

      //bind click event
      d3.selectAll("[role='calibration'] [name='displayType']").on("click", function(){
        renderColor();
      });
    }

    function renderColor(){
      var renderByCount = document.getElementsByName("displayType")[0].checked;

      rect
        .filter(function(d){
          return (d.value["W"] >= 0);
        })
        .transition()
        .delay(function(d){
          return (dayFormat(d.date)-dayOffset) * 15;
        })
        .duration(500)
        .attrTween("fill", function(d, i, a){
          //choose color dynamically
          var colorIndex = d3.scale.quantize()
            .range([0, 1, 2, 3, 4, 5, 6, 7, 8])
            .domain((renderByCount?[0, 1]:dailyValueExtent[d.day]));

          return d3.interpolate(a, colorCalibration[colorIndex(d.value["W"])]);
        });
    }
  }

  function drawBarGraph() {
    var margin = {top: 20, right: 20, bottom: 30, left: 35},
        width = 1600 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .tickPadding(30)
        .ticks(10, "Päiväys")
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10, "kW");

    var svg = d3.select("[role=bargraph]")
        .attr("width", 1545)
//        width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.json("/homecontroller/electricity/get_barchart_json", function(error, data) {
      x.domain(data.map(function(d) { return d.date; }));
      y.domain([0, d3.max(data, function(d) { return d.consumption; })]);

      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("Kulutus");

      svg.selectAll(".bar")
          .data(data)
        .enter().append("rect")
          .attr("class", "bar")
          .attr("x", function(d) { return x(d.date); })
          .attr("width", x.rangeBand())
          .attr("y", function(d) { return y(d.consumption); })
          .attr("height", function(d) { return height - y(d.consumption); });

    });

    function type(d) {
      d.frequency = +d.frequency;
      return d;
    }
  }

  this.drawHeatmap = drawHeatmap;
  this.drawBarGraph = drawBarGraph;
};


var electricity_info;
jq(document).ready(function () {
  "use strict";
  electricity_info = new ElectricityInfo();

  jq(".main-button-box .electricity").on("click", function() {
    electricity_info.drawHeatmap();
    electricity_info.drawBarGraph();
    content_switch.switchContent("#electricity-modal");
  });
  jq("#electricity-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
    jq("#electricity-modal .heatmap").children().remove(); // Clean up graph
    jq("#electricity-modal .bargraph").children().remove(); // Clean up graph

  });
});
