var refresh_weather = function () {
  function set_weather_info (elem, info) {
    $(elem).html("<img src='/homecontroller/static/images/"+info.fields.icon+".png'> "+info.fields.temperature+"&deg;C");
  }

  function reset_weather_info() {
    $("#weather-general").html("<i class='fa fa-question-circle'></i>");
  }
  $.get("/homecontroller/weather/get_json", function (data) {
    reset_weather_info();
    var first_date = moment(), plus_one = false;
    var hour = parseInt(first_date.format("H")) + 1;
    if (hour >= 23) {
      first_date = first_date.add(1, "days");
      plus_one = true;
      hour = 0;
    }
    var today = first_date.format("YYYY-MM-DD");
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
