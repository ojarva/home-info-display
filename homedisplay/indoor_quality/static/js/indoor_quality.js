var IndoorAirQuality = function (options) {
  "use strict";
  options = options || {};
  options.main_elem = options.main_elem || ".indoor-quality";
  options.update_timeout = options.update_timeout || 2 * 60 * 1000;
  options.co2_green = options.co2_green || 1000;
  options.co2_error = options.co2_error || 1500;

  var output = jq(options.main_elem),
      update_interval,
      update_timeout;

  function clearAutoNoUpdates() {
    if (update_timeout) {
      update_timeout = clearTimeout(update_timeout);
    }
  }

  function autoNoUpdates() {
    output.find(".status").html("<i class='fa fa-times warning-message'></i> ");
  }

  function drawGraph(data, goptions) {
    goptions = goptions || {};
    goptions.xlabel = goptions.xlabel || "Aika";
    goptions.ylabel = goptions.ylabel || "Arvo";

    var elem = jq(goptions.selector);

    if (typeof data === "undefined") {
      debug.warn("No data available for indoor air quality graphs");
      console.warn("!!! No data available for indoor air quality graphs!");
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
      .y(function(d, i) { return d[1]; });

      chart.xAxis
      .axisLabel(goptions.xlabel)
      .tickFormat(function(d) {
        return d3.time.format("%H:%M")(new Date(d));
      });

      chart.yAxis     //Chart y-axis settings
      .axisLabel(goptions.ylabel)
      .tickFormat(d3.format(".02f"));

      var processed_data = [];
      jq.each(data, function () {
        processed_data.push([this.timestamp, this.value]);
      });
      processed_data.reverse();
      var myData = [{"key": goptions.key,
                     "bar": true,
                     "color": "#ccf",
                     "values": processed_data
                   }];

      d3.select(goptions.selector)    //Select the <svg> element you want to render the chart in.
      .datum(myData)         //Populate the <svg> element with chart data...
      .call(chart);          //Finally, render the chart!

      //Update the chart when window resizes.
      nv.utils.windowResize(chart.update);
      return chart;
    });
  }

  function processCo2(data) {
    if (typeof data === "undefined") {
      console.warn("!!! No indoor air quality information available.");
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
    var previous_reading = output.find(".co2").data("value");
    if (previous_reading) {
      if (previous_reading < co2) {
        // Gone up
        output.find(".co2").effect("highlight", {color: "red"}, 150);
      } else if (previous_reading > co2) {
        // Gone down
        output.find(".co2").effect("highlight", {color: "green"}, 150);
      }
    }
    output.find(".co2").data("value", co2).html(Math.round(co2) + "ppm");
    clearAutoNoUpdates();
    update_timeout = setTimeout(autoNoUpdates, options.update_timeout); // 2,5 minutes
  }

  function processTemperature(data) {
    if (typeof data === "undefined") {
      console.warn("!!! No indoor air quality information available.");
      autoNoUpdates();
      return;
    }
    var temperature = data.value;
    var previous_reading = output.find(".temperature").data("value");
    if (previous_reading) {
      if (previous_reading < temperature) {
        // Gone up
        output.find(".temperature").effect("highlight", {color: "red"}, 150);
      } else if (previous_reading > temperature) {
        // Gone down
        output.find(".temperature").effect("highlight", {color: "green"}, 150);
      }
    }
    output.find(".temperature").data("value", temperature).html(Math.round(parseFloat(temperature) * 10) / 10 + "&deg;C");
  }

  function fetch() {
    jq.get("/homecontroller/indoor_quality/get_latest/co2", function (data) {
      processCo2(data);
    });
    jq.get("/homecontroller/indoor_quality/get_latest/temperature", function (data) {
      processTemperature(data);
    });
  }

  function fetchTrend() {
    jq.get("/homecontroller/indoor_quality/get_json/co2/trend", function (data) {
      if (data.status === "no_data") {
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
    update();
    update_timeout = setTimeout(autoNoUpdates, 5000);
    ws_generic.register("indoor_quality", fetchTrend); // TODO: trend should be updated without polling
    ws_generic.register("indoor_co2", processCo2);
    ws_generic.register("indoor_temperature", processTemperature);
    ge_refresh.register("indoor_quality", update);
  }

  function stopInterval() {
    ws_generic.deRegister("indoor_quality");
    ws_generic.deRegister("indoor_co2");
    ws_generic.deRegister("indoor_temperature");
    ge_refresh.deRegister("indoor_quality");
  }

  function refreshData(key) {
    var data_output = jq(".indoor-air-" + key);
    data_output.find("svg").hide();
    data_output.find(".spinner").show();
    jq.get("/homecontroller/indoor_quality/get_json/"+key, function(data) {
      if (data.length > 12) {
        data_output.find(".latest").html(Math.round(data[data.length-1].value * 10) / 10);
        data_output.find(".data-error").hide();
        data_output.find(".spinner").hide();
        data_output.find("svg").show();
        drawGraph(data, {key: key, selector: ".indoor-air-" + key + " svg"});
      } else {
        data_output.find(".latest").html("-");
        data_output.find("svg").slideUp();
        data_output.find(".spinner").slideUp();
        data_output.find(".data-error").slideDown();
      }
    });
  }

  function refreshAllData() {
    jq.get("/homecontroller/indoor_quality/get_keys", function(data) {
      jq.each(data, function () {
        refreshData(this);
      });
    });
  }

  this.fetch = fetch;
  this.fetchTrend = fetchTrend;
  this.refreshData = refreshData;
  this.refreshAllData = refreshAllData;
  this.drawGraph = drawGraph;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var indoor_air_quality;
var indoor_air_quality_modal_timeout;

function closeIndoorAirQualityModal() {
  "use strict";
  jq("#indoor-quality-modal .close").trigger("click");
}

jq(document).ready(function () {
  "use strict";
  indoor_air_quality = new IndoorAirQuality();
  indoor_air_quality.startInterval();

  jq(".indoor-quality").on("click", function () {
    jq.get("/homecontroller/indoor_quality/get_modal", function (data) {
      jq("#indoor-quality-modal .air-quality-graph-content").html(data);
      indoor_air_quality.refreshAllData();
      content_switch.switchContent("#indoor-quality-modal");
    });
  });

  jq("#indoor-quality-modal .close").on("click", function() {
    jq("#indoor-quality-modal .air-quality-graph-content").children().remove();
    content_switch.switchContent("#main-content");
    indoor_air_quality_modal_timeout = clearTimeout(indoor_air_quality_modal_timeout);
  });
});
