
$(document).ready(function () {
  function set_weather_info (elem, text, info) {
    $(elem).html(text+"<br>"+info.fields.temperature+"&deg;C <img src='/static/images/"+info.fields.icon+".png'>");
  }

  function reset_weather_info() {
    $(".weather-info .col-md-4").each(function () {
      $(this).html("<br><i class='fa fa-question'></i>");
    })
  }
  $.get("/weather/get_json", function (data) {
    reset_weather_info();
    var first_date = moment();
    var hour = parseInt(first_date.format("H"));
    if (hour >= 23) {
      first_date = first_date.add(1, "days");
      hour = 0;
    }
    var today = first_date.format("YYYY-MM-DD");
    var tomorrow = first_date.add(1, "days").format("YYYY-MM-DD");
    $.each(data, function () {
      var set = false;
      var this_text, this_elem;
      console.log(this.fields.date, tomorrow, today);
      if (this.fields.date == today) {
        // Current day
        if (this.fields.hour == hour) {
          set = true;
          this_elem = "#today .weather-1";
          this_text = "Nyt";
        } else if (this.fields.hour == hour + 2) {
          set = true;
          this_elem = "#today .weather-2";
          this_text = "2h";
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
        set_weather_info(this_elem, this_text, this);
      }
      console.log(this.fields.date);
    });
  });

});
