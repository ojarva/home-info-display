var IndoorAirQuality = function (options) {
  options = options || {};
  options.main_elem = options.main_elem || "#indoor-quality";

  var output = $(options.main_elem),
      latest_data,
      update_interval,
      update_timeout,
      ws4redis;

  function onReceiveItemWS(message) {
    if (message == "updated") {
      console.log("indoor air quality: backend requests update");
      update();
    }
  }

  function clearAutoNoUpdates() {
    if (update_timeout) {
      update_timeout = clearTimeout(update_timeout);
    }
  }

  function autoNoUpdates() {
    output.find(".status").html("<i class='fa fa-times warning-message'></i> Ei tietoja");
  }

  function getData() {
    return latest_data;
  }

  function fetch() {
    $.get("/homecontroller/indoor_quality/co2", function (data) {
      var latest = data[0];
      if (typeof latest == "undefined") {
        console.log("!!! No indoor air quality information available.");
        autoNoUpdates();
        return;
      }
      var co2 = latest.fields.co2;
      var co2_out;
      if (co2 < 1000) {
        co2_out = "<i class='fa fa-check success-message'></i>";
        output.removeClass("warning-message error-message");
      } else if (co2 < 1500) {
        co2_out = "<i class='fa fa-exclamation-triangle'></i>";
        output.addClass("warning-message");
      } else {
        co2_out = "<i class='fa fa-ban'></i>";
        output.addClass("error-message");
      }
      output.find(".status").html(co2_out);
      output.find(".temperature").html(Math.round(parseFloat(latest.fields.temperature)*10)/10+"&deg;C");
      output.find(".co2").html(co2+"ppm");
      $("#indoor-quality-modal .latest-indoor-co2").html(co2);
      $("#indoor-quality-modal .latest-indoor-temperature").html((parseFloat(latest.fields.temperature)*10)/10);
      clearAutoNoUpdates();
      update_timeout = setTimeout(autoNoUpdates, 150000); // 2,5 minutes
      latest_data = data;
    });
  }

  function drawGraph(data) {
    // TODO: remove code duplication.
    if (typeof data == "undefined") {
      console.log("!!! No data available for indoor air quality graphs!");
      return;
    }
    var x = [];
    var y = [];
    nv.addGraph(function() {
      var chart = nv.models.lineChart()
      .useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
      .showLegend(false)
      .interpolate("bundle")
      .transitionDuration(350)  //how fast do you want the lines to transition?
      .showYAxis(true)        //Show the y-axis
      .showXAxis(true)        //Show the x-axis
      .x(function(d, i) { return (new Date(d[0]).getTime()); })
      .y(function(d, i) { return d[1]; })
      ;

      chart.xAxis
      .axisLabel("Time")
      .tickFormat(function(d) {
        return d3.time.format('%H:%M')(new Date(d))
      });

      chart.yAxis     //Chart y-axis settings
      .axisLabel('CO2 (ppm)')
      .tickFormat(d3.format('.02f'));

      processed_data = []
      $.each(data, function () {
        processed_data.push([this.fields.timestamp, this.fields.co2]);
      });
      processed_data.reverse();
      var myData = [{"key": "CO2",
                     "bar": true,
                     "color": "#ccf",
                     "values": processed_data
                   }];

      d3.select('#indoor-air-quality-co2-graph svg')    //Select the <svg> element you want to render the chart in.
      .datum(myData)         //Populate the <svg> element with chart data...
      .call(chart);          //Finally, render the chart!

      //Update the chart when window resizes.
      nv.utils.windowResize(chart.update);
      return chart;
    });

    var x = [];
    var y = [];
    nv.addGraph(function() {
      var chart = nv.models.lineChart()
      .useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
      .showLegend(false)
      .interpolate("bundle")
      .transitionDuration(350)  //how fast do you want the lines to transition?
      .showYAxis(true)        //Show the y-axis
      .showXAxis(true)        //Show the x-axis
      .x(function(d, i) { return (new Date(d[0]).getTime()); })
      .y(function(d, i) { return d[1]; })
      ;

      chart.xAxis
      .axisLabel("Time")
      .tickFormat(function(d) {
        return d3.time.format('%H:%M')(new Date(d))
      });

      chart.yAxis     //Chart y-axis settings
      .axisLabel('CO2 (ppm)')
      .tickFormat(d3.format('.02f'));

      processed_data = []
      $.each(data, function () {
        processed_data.push([this.fields.timestamp, this.fields.temperature]);
      });
      processed_data.reverse();
      var myData = [{"key": "Temperature",
                     "bar": true,
                     "color": "#ccf",
                     "values": processed_data
                   }];

      d3.select('#indoor-air-quality-temperature-graph svg')    //Select the <svg> element you want to render the chart in.
      .datum(myData)         //Populate the <svg> element with chart data...
      .call(chart);          //Finally, render the chart!

      //Update the chart when window resizes.
      nv.utils.windowResize(chart.update);
      return chart;
    });
  }

  function fetchTrend() {
    $.get("/homecontroller/indoor_quality/co2/trend", function (data) {
      if (data.status == "no_data") {
        output.find(".trend").html("");
        return;
      }
      var icon;
      if (data.delta < -0.025) {
        icon = "down";
      } else if (data.delta > 0.025) {
        icon = "up";
      } else {
        icon = "right";
      }
      output.find(".trend").html("<i class='fa fa-arrow-"+icon+"'></i>");
    });
  }

  function update() {
    fetch();
    fetchTrend();
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, 1800000);
    ws4redis = new WS4Redis({
      uri: websocket_root+'indoor?subscribe-broadcast&publish-broadcast&echo',
      receive_message: onReceiveItemWS,
      heartbeat_msg: "--heartbeat--"
    });
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    try {
      ws4redis.close();
    } catch(e) {

    }
  }

  this.fetch = fetch;
  this.getData = getData;
  this.fetchTrend = fetchTrend;
  this.drawGraph = drawGraph;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var indoor_air_quality;
$(document).ready(function () {
  indoor_air_quality = new IndoorAirQuality();
  indoor_air_quality.startInterval();

  $("#indoor-quality").on("click", function () {
    indoor_air_quality.drawGraph(indoor_air_quality.getData());
    switchVisibleContent("#indoor-quality-modal");
  });

  $("#indoor-quality-modal .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
