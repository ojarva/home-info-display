var RefreshWeather = function (options) {
  "use strict";
  options = options || {};

  function resetWeatherInfo() {
    jq(".weather .weather-box span").html("<i class='fa fa-question-circle'></i>");
    jq(".weather .data-field").html("<i class='fa fa-question-circle'></i>");
    jq(".weather .weather-box").removeClass("new-day"); // Remove "day changed" separator line
    jq(".weather-all").children().remove();
  }

  function processData(data) {
    resetWeatherInfo();
    debug.log("Processing weather data with " + data.hours.length + " items");
    if (data.sun !== undefined) {
      var sunrise = moment(data.sun.sunrise);
      var sunset = moment(data.sun.sunset);
      jq(".sun-info").html("<i class='fa fa-sun-o'></i><i class='fa fa-long-arrow-up'></i> " + sunrise.format("HH:mm") + " (<span class='auto-fromnow-update' data-timestamp='" + sunrise + "'>" + sunrise.fromNowSynced() + "</span>) <i class='fa fa-sun-o'></i><i class='fa fa-long-arrow-down'></i> " + sunset.format("HH:mm") + " (<span class='auto-fromnow-update' data-timestamp='" + sunset + "'>" + sunset.fromNowSynced() + "</span>)");
    }
    var items = jq(".weather"),
        current_index = 1,
        first_date = false,
        new_day = false;
    if (data !== undefined && data.current !== null && data.current.feels_like !== null) {
      items.find(".temperature-now").html(data.current.feels_like);
      items.find(".wind-now").html(data.current.wind_speed_readable);
      var direction = (data.current.wind_direction_degrees + "").replace(".", "_");
      items.find(".wind-direction-now").html("<i class='fa fa-fw fa-long-arrow-up fa-rotate-"+direction+"'></i>");
    }
    jq.each(data.next, function () {
      var this_item = items.find(".weather-" + current_index);
      if (first_date === false) {
        first_date = this.item.date;
      } else if (new_day === false) {
        if (first_date !== this.item.date) {
          this_item.addClass("new-day");
          new_day = true;
        }
      }
      this_item.find(".timestamp").html(this.name);
      this_item.find(".temperature").html(this.item.feels_like);
      this_item.find(".symbol").html("<img src='/homecontroller/static/images/" + this.item.icon + ".png'>");
      this_item.find(".temperature-unit").html("&deg;C");
      current_index += 1;
    });
    current_index = 13;

    var now = clock.getMoment(),
        current_row,
        highlight_set = false,
        last_header,
        new_item = "<div class='col-md-1'><span class='timestamp'><i class='fa fa-question-circle'></i></span><br><span class='temperature'><i class='fa fa-question-circle'></i></span><span class='temperature-unit'>&deg;C</span><span class='symbol'><i class='fa fa-question-circle'></i></span><br><span class='wind-direction'></span><span> </span> <span class='wind-speed'><i class='fa fa-question-circle'></i></span><span class='wind-speed-unit'>m/s</span></div>";
    jq.each(data.hours, function () {
      if (this.hour % 2 !== 0) {
        return true; // continue
      }
      if (current_index > 11) {
        current_index = 0;
        jq(".weather-all").append("<div class='row'><div class='col-md-12'><h2></h2></div></div><div class='row'></div>");
        current_row = jq(".weather-all .row").last();
        last_header = jq(".weather-all h2").last();
        last_header.html(this.weekday_fi + " " + this.date);
      }
      current_row.append(new_item);
      var current_item = current_row.find(".col-md-1").last();

      current_item.find(".timestamp").html(this.hour + ":00");
      current_item.find(".temperature").html(this.feels_like);
      current_item.find(".symbol").html("<img src='/homecontroller/static/images/" + this.icon + ".png'>");
      current_item.find(".temperature-unit").html("&deg;C");
      current_item.find(".wind-speed").html(Math.round(this.wind_speed / 3.6));
      if (this.wind_direction_degrees !== null) {
        var direction = (this.wind_direction_degrees + "").replace(".", "_");
        current_item.find(".wind-direction").html("<i class='fa fa-fw fa-long-arrow-up fa-rotate-"+direction+"'></i>");
      }
      if (!highlight_set && this.date === now.format("YYYY-MM-DD") && (now.hour() === this.hour || now.hour() - 1 === this.hour)) {
        current_item.addClass("weather-today");
        highlight_set = true;
      }
      current_index += 1;
    });
  }

  function update() {
    jq.get("/homecontroller/weather/get_json", function (data) {
      processData(data);
    });
  }

  function onReceiveItemWS(data) {
    processData(data);
  }

  function startInterval() {
    update();
    ws_generic.register("weather", onReceiveItemWS);
    ge_refresh.register("weather", update);
    ge_intervals.register("weather", "hourly", update);
  }

  function stopInterval() {
    ws_generic.deRegister("weather");
    ge_refresh.deRegister("weather");
    ge_intervals.deRegister("weather", "hourly");
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;

};

var refresh_weather;
jq(document).ready(function () {
  "use strict";
  refresh_weather = new RefreshWeather();
  refresh_weather.startInterval();
  jq(".open-weather-modal").on("click", function() {
    content_switch.switchContent("#weather-modal");
  });
  jq("#weather-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
