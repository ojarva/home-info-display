var RefreshWeather = function (options) {
  options = options || {};
  options.update_interval = options.update_interval || 1000 * 60 * 120;
  var update_interval;

  function setWeatherInfo (elem, text, info) {
    $(elem).html(text+"<br><span class='weather-temperature'>" + info.fields.apparent_temperature + "&deg;C</span> <img src='/homecontroller/static/images/" + info.fields.icon + ".png'>");
  }

  function resetWeatherInfo() {
    $(".weather .weather-box span").html("<i class='fa fa-question-circle'></i>");
    $(".weather .data-field").html("<i class='fa fa-question-circle'></i>");
  }

  function processData(data) {
    resetWeatherInfo();
    if (data.sun) {
      var sunrise = moment(data.sun.sunrise);
      var sunset = moment(data.sun.sunset);
      $(".sun-info").html("<i class='fa fa-sun-o'></i><i class='fa fa-long-arrow-up'></i> " + sunrise.format("HH:mm") + " (<span class='auto-fromnow-update' data-timestamp='" + sunrise + "'>" + sunrise.fromNow() + "</span>) <i class='fa fa-sun-o'></i><i class='fa fa-long-arrow-down'></i> " + sunset.format("HH:mm") + " (<span class='auto-fromnow-update' data-timestamp='" + sunset + "'>" + sunset.fromNow() + "</span>)");
    }
    var items = $(".weather"),
        current_index = 1,
        first_date = false,
        new_day = false;
    items.find(".temperature-now").html(data.current.apparent_temperature);
    items.find(".wind-now").html(data.current.wind_speed_readable);
    $.each(data.next, function () {
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
      this_item.find(".temperature").html(this.item.apparent_temperature);
      this_item.find(".symbol").html("<img src='/homecontroller/static/images/" + this.item.icon + ".png'>");
      this_item.find(".temperature-unit").html("&deg;C");
      current_index += 1;
    });
  }

  function update() {
    $.get("/homecontroller/weather/get_json", function (data) {
      processData(data);
    });
  }

  function onReceiveItemWS(data) {
    processData(data);
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, options.update_interval);
    ws_generic.register("weather", onReceiveItemWS);
    ge_refresh.register("weather", update);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    ws_generic.deRegister("weather");
    ge_refresh.deRegister("weather");
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;

};

var refresh_weather;
$(document).ready(function () {
  refresh_weather = new RefreshWeather();
  refresh_weather.startInterval();
});
