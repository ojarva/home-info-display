var IndoorAirQuality = function (options) {
  options = options || {};
  options.main_elem = options.main_elem || ".indoor-quality";
  options.update_interval = options.update_interval || 1800000;
  options.update_timeout = options.update_timeout || 360000;
  options.co2_green = options.co2_green || 1000;
  options.co2_error = options.co2_error || 1500;

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
    $.get("/homecontroller/indoor_quality/get_latest/co2", function (data) {
      if (typeof data == "undefined") {
        console.log("!!! No indoor air quality information available.");
        autoNoUpdates();
        return;
      }
      var co2 = data.value;
      var co2_out;
      if (co2 < options.co2_green) {
        co2_out = "<i class='fa fa-check success-message'></i>";
        output.removeClass("warning-message error-message");
      } else if (co2 < options.co2_error) {
        co2_out = "<i class='fa fa-exclamation-triangle'></i>";
        output.removeClass("error-message").addClass("warning-message");
      } else {
        co2_out = "<i class='fa fa-ban'></i>";
        output.removeClass("warning-message").addClass("error-message");
      }
      output.find(".status").html(co2_out);
      output.find(".co2").html(Math.round(co2)+"ppm");
      clearAutoNoUpdates();
      update_timeout = setTimeout(autoNoUpdates, options.update_timeout); // 2,5 minutes
      latest_data = data;
    });
    $.get("/homecontroller/indoor_quality/get_latest/temperature", function (data) {
      if (typeof data == "undefined") {
        console.log("!!! No indoor air quality information available.");
        autoNoUpdates();
        return;
      }
      var temperature = data.value;
      output.find(".temperature").html(Math.round(parseFloat(temperature)*10)/10+"&deg;C");
    });
  }

  function drawGraph(data, options) {
    options = options || {};
    options.xlabel = options.xlabel || "Aika";
    options.ylabel = options.ylabel || "Arvo";

    elem = $(options.selector);

    if (typeof data == "undefined") {
      console.log("!!! No data available for indoor air quality graphs!");
      elem.children().remove();
      elem.slideUp();
      elem.parent().find(".data-error").slideDown();
      return;
    } else {
      elem.slideDown();
      elem.parent().find(".data-error").slideUp();
    }
    /*
      options.ylabel
      options.key
      options.selector
      options.field_selector
    */
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
      .axisLabel(options.xlabel)
      .tickFormat(function(d) {
        return d3.time.format('%H:%M')(new Date(d))
      });

      chart.yAxis     //Chart y-axis settings
      .axisLabel(options.ylabel)
      .tickFormat(d3.format('.02f'));

      processed_data = []
      $.each(data, function () {
        processed_data.push([this.timestamp, this.value]);
      });
      processed_data.reverse();
      var myData = [{"key": options.key,
                     "bar": true,
                     "color": "#ccf",
                     "values": processed_data
                   }];

      d3.select(options.selector)    //Select the <svg> element you want to render the chart in.
      .datum(myData)         //Populate the <svg> element with chart data...
      .call(chart);          //Finally, render the chart!

      //Update the chart when window resizes.
      nv.utils.windowResize(chart.update);
      return chart;
    });
  }


  function fetchTrend() {
    $.get("/homecontroller/indoor_quality/get_json/co2/trend", function (data) {
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
    update_interval = setInterval(update, options.update_interval);
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

  function refreshAllData() {
    $.get("/homecontroller/indoor_quality/get_keys", function(data) {
      $.each(data, function () {
        refreshData(this);
      });
    });
  }
  function refreshData(key) {
    var data_output = $(".indoor-air-"+key);
    data_output.find("svg").hide();
    data_output.find(".spinner").show();
    $.get("/homecontroller/indoor_quality/get_json/"+key, function(data) {
      if (data[0]) {
        data_output.find(".latest").html(Math.round(data[0].value*10)/10);
      }
      data_output.find("svg").show();
      data_output.find(".spinner").hide();

      drawGraph(data, {key: key, selector: ".indoor-air-"+key+" svg"});
    });
  }

  this.fetch = fetch;
  this.getData = getData;
  this.fetchTrend = fetchTrend;
  this.refreshData = refreshData;
  this.refreshAllData = refreshAllData;
  this.drawGraph = drawGraph;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var indoor_air_quality;
$(document).ready(function () {
  indoor_air_quality = new IndoorAirQuality();
  indoor_air_quality.startInterval();

  $(".indoor-quality").on("click", function () {
    $.get("/homecontroller/indoor_quality/get_modal", function (data) {
      $("#indoor-quality-modal .air-quality-graph-content").html(data);
      indoor_air_quality.refreshAllData()
      switchVisibleContent("#indoor-quality-modal");
    });
  });

  $("#indoor-quality-modal .close").on("click", function() {
    $("#indoor-quality-modal .air-quality-graph-content").children().remove();
    switchVisibleContent("#main-content");
  });
});
