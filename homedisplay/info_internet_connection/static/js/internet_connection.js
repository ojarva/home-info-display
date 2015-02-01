function refresh_internet() {
  $.get("/homecontroller/internet_connection/status", function (data) {
    data = data[0];
    output = $("#internet_connection");
    var cs = data.fields.connect_status;
    var cs_out;
    if (cs == "connected") {
      cs_out = "<i class='fa fa-check-circle success-message'></i>";
    } else if (cs == "connecting") {
      cs_out = "<i class='fa fa-spin fa-cog warning-message'></i>";
    } else {
      cs_out = "<i class='fa fa-times error-message'></i>";
    }
    output.find("#connected").html(cs_out);
    output.find("#mode").html(data.fields.mode);
    output.find("#signal").html(data.fields.signal+"/5");
    data_moment = moment(data.fields.timestamp);
    output.find("#age").html("("+data_moment.fromNow()+")");
  });
}

$(document).ready(function() {
  refresh_internet();
  setInterval(refresh_internet, 60000);
});
