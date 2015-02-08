var RefreshWeather = function () {
  var ws4redis, update_interval;

  function set_weather_info (elem, text, info) {
    $(elem).html(text+"<br><span class='weather-temperature'>"+info.fields.apparent_temperature+"&deg;C</span> <img src='/homecontroller/static/images/"+info.fields.icon+".png'>");
  }

  function reset_weather_info() {
    $(".weather-info .col-md-4").each(function () {
      $(this).html("<br><i class='fa fa-question-circle'></i>");
    })
  }

  function update() {
    $.get("/homecontroller/weather/get_json", function (data) {
      reset_weather_info();
      var first_date = moment(), plus_one = false, hour, today, tomorrow, desired_hours = {};
      hour = parseInt(first_date.format("H"));
      if (hour >= 23) {
        first_date = first_date.add(1, "days");
        plus_one = true;
        hour = 0;
      }
      today = first_date.format("YYYY-MM-DD");
      tomorrow = first_date.add(1, "days").format("YYYY-MM-DD");
      desired_hours = {};
      if (hour < 6) {
        desired_hours[8] = {"this_elem": "#today .weather-2", "this_text": "Aamu"};
        desired_hours[16] = {"this_elem": "#today .weather-3", "this_text": "Iltapäivä"};
      } else if (hour < 12) {
        desired_hours[16] = {"this_elem": "#today .weather-2", "this_text": "Iltapäivä"};
        desired_hours[19] = {"this_elem": "#today .weather-3", "this_text": "Ilta"};
      } else if (hour < 18) {
        desired_hours[20] = {"this_elem": "#today .weather-2", "this_text": "Ilta"};
        desired_hours[23] = {"this_elem": "#today .weather-3", "this_text": "Yö"};
      } else if (hour < 23) {
        desired_hours[23] = {"this_elem": "#today .weather-2", "this_text": "Yö"};
      }
      $.each(data, function () {
        var set = false, this_text, this_elem, this_data = this;
        if (this.fields.date == today) {
          // Current day
          if (this.fields.hour == hour) {
            set = true;
            this_elem = "#today .weather-1";
            this_text = "Nyt";
          } else {
            for (var key in desired_hours) {
              if (key == this.fields.hour) {
                this_elem = desired_hours[key]["this_elem"];
                this_text = desired_hours[key]["this_text"];
                set = true;
              }
            }
          }
        } else if (this.fields.date == tomorrow) {
          // Next day
          if (this.fields.hour == 8) {
            set = true;
            this_elem = "#tomorrow .weather-1";
            this_text = "Aamu";
          } else if (this.fields.hour == 16) {
            set = true;
            this_elem = "#tomorrow .weather-2";
            this_text = "Iltapäivä";
          } else if (this.fields.hour > 18) {
            set = true;
            this_elem = "#tomorrow .weather-3";
            this_text = "Ilta";
          }
        }
        if (set) {
          if (plus_one) {
            this_text += " (+1)";
          }
          set_weather_info(this_elem, this_text, this_data);
        }
      });
    });
  }

  function onReceiveItemWS(message) {
    if (message == "updated") {
      console.log("weather: backend requests update");
      update();
    }
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, 1800000);
    ws4redis = new WS4Redis({
      uri: websocket_root+'weather?subscribe-broadcast&publish-broadcast&echo',
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

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;

};

var refresh_weather;
$(document).ready(function () {
  refresh_weather = new RefreshWeather();
  refresh_weather.startInterval();
});
