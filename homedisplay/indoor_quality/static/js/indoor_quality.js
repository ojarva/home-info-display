function fetch_indoor_quality() {
  $.get("/homecontroller/indoor_quality/co2", function (data) {
    var latest = data[0];
    var co2 = latest.fields.co2;
    var co2_out;
    if (co2 < 1000) {
      co2_out = "<i class='fa fa-check success-message'></i>";
      $("#indoor-quality").removeClass("warning-message error-message");
    } else if (co2 < 1500) {
      co2_out = "<i class='fa fa-exclamation-triangle'></i>";
      $("#indoor-quality").addClass("warning-message");
    } else {
      co2_out = "<i class='fa fa-ban'></i>";
      $("#indoor-quality").addClass("error-message");
    }
    $("#indoor-quality .status").html(co2_out);
    $("#indoor-quality .temperature").html(temperature+"&deg;C");
    $("#indoor-quality .co2").html(co2+"ppm");
  });
}

$(document).ready(function () {
  fetch_indoor_quality();
  setInterval(fetch_indoor_quality, 60000);
});
