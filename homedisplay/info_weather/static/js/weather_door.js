var RefreshWeather = function (options) {
  "use strict";
  options = options || {};
  options.elem = options.elem || "#weather-general";
  options.update_interval = options.update_interval || FAST_UPDATE;
  var elem = $(options.elem),
      update_interval;
  function setWeatherInfo (icon, temperature) {
    elem.html("<img src='/homecontroller/static/images/" + icon + ".png'><br> " + temperature + "&deg;C");
  }

  function resetWeatherInfo() {
    elem.html("<i class='fa fa-question-circle'></i>");
  }

  function update() {
    $.get("/homecontroller/weather/get_json?" + (new Date()).getTime(), function (data) {
      resetWeatherInfo();
      if (data && data.current) {
        setWeatherInfo(data.current.icon, data.current.feels_like);
      }
    });
  }

  function startInterval() {
    update();
    update_interval = setInterval(update, options.update_interval);
  }

  function stopInterval() {
    update_interval = clearInterval(update_interval);
  }

  this.update = update;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var refresh_weather;

$(document).ready(function () {
  "use strict";
  refresh_weather = new RefreshWeather({"elem": "#weather-general"});
  refresh_weather.startInterval();
});
