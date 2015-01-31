
$(document).ready(function () {
  function set_weather_info (elem, info) {

    $(elem).html("Nyt<br>"+info.fields.temperature+"&deg;C <img src='/static/images/"+info.fields.icon+".png'");
  }
  $.get("/weather/get_json", function (data) {
    var first_date = moment();
    var hour = parseInt(first_date.format("H"))
    if (hour > 23) {
      first_date = first_date.add(1, "days");
      hour = 0;
    }
    var tomorrow = first_date.add(1, "days").format("YYYY-MM-DD");
    var today = first_date.format("YYYY-MM-DD");
    $.each(data, function () {
      if (this.fields.date == today) {
        // Current day
        if (this.fields.hour == hour) {
          console.log("!!!");
          set_weather_info("#today .weather-1", this);
        }
      } else if (this.fields.date == tomorrow) {
        // Next day
      }
      console.log(this.fields.date);
    });
  });

});
