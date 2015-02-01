function refresh_internet() {
    $.get("/homecontroller/internet_connection/status", function (data) {
        console.log(data);
        output = $("#internet_connection");
        output.find("#connected").html(data.fields.connect_status);
        output.find("#mode").html(data.fields.mode);
        output.find("#signal").html(data.fields.signal+"/5");
        data_moment = moment(data.fields.timestamp);
        output.find("#age").html(data_moment.fromnow());
    });
}

$(document).ready(function() {
  refresh_internet();
  setInterval(refresh_internet, 60000);
});
