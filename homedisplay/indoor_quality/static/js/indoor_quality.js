function fetch_indoor_quality() {
  var output = $("#indoor-quality");
  $.get("/homecontroller/indoor_quality/co2", function (data) {
    var latest = data[0];
    var co2 = latest.fields.co2;
    var co2_out;
    if (co2 < 1000) {
      co2_out = "<i class='fa fa-check success-message'></i>";
      output.removeClass("warning-message error-message");
    } else if (co2 < 1500) {
      co2_out = "<i class='fa fa-exclamation-triangle'></i>";
      output.addClass("warning-message");
    } else {
      co2_out = "<i class='fa fa-ban'></i>";
      output.addClass("error-message");
    }
    output.find(".status").html(co2_out);
    output.find(".temperature").html(Math.round(parseFloat(latest.fields.temperature)*10)/10+"&deg;C");
    output.find(".co2").html(co2+"ppm");
    data_moment = moment(data.fields.timestamp);
    output.find(".age").html("("+data_moment.fromNow()+")");
  });
  $.get("/homecontroller/indoor_quality/co2/trend", function (data) {
    var icon;
    if (data.delta < -0.05) {
      icon = "down";
    } else if (data.delta > 0.05) {
      icon = "up";
    } else {
      icon = "right";
    }
    output.find(".trend").html("<i class='fa fa-arrow-"+icon+"'></i>");
  });
}

$(document).ready(function () {
  fetch_indoor_quality();
  setInterval(fetch_indoor_quality, 60000);
});
