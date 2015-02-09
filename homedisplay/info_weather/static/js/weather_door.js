var refresh_weather = function () {
  function set_weather_info (elem, info) {
    $(elem).html("<img src='/homecontroller/static/images/"+info.fields.icon+".png'><br> "+info.fields.apparent_temperature+"&deg;C");
  }

  function reset_weather_info() {
    $("#weather-general").html("<i class='fa fa-question-circle'></i>");
  }
  $.get("/homecontroller/weather/get_json", function (data) {
    reset_weather_info();
    var current_time = moment().add(1, "hours");
    var today = current_time.format("YYYY-MM-DD");
    var hour = current_time.format("H")
    $.each(data, function () {
      var this_data = this;
      if (this.fields.date == today) {
        // Current day
        if (this.fields.hour == hour) {
          set_weather_info("#weather-general", this_data);
          return false;
        }
      }
    });
  });
}
$(document).ready(function () {
  refresh_weather();
  setInterval(refresh_weather, 300000); // 5 minutes
});
