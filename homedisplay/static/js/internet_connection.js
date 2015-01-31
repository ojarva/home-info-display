function refresh_internet() {
    $.get("/homecontroller/internet_connection/status", function (data) {
        console.log(data);
        output = $("#internet_connection");
        output.find("#connected").html(data.connected);
        output.find("#mode").html(data.mode);
        output.find("#signal").html(data.signal+"/5");
    //    $("#internet_connection")
    });
}

$(document).ready(function() {
    $.get("/homecontroller/internet_connection/content", function(data) {
        $("#internet_connection").html(data);
        refresh_internet();
        setInterval(refresh_internet, 60000);
    });
});
