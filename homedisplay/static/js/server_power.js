function refresh_server_power() {
    $.get("/server_power/status", function (data) {
        $("#server_power").html(data);
        $(".server_power_shutdown").click(function () {
            $.get("/server_power/shutdown");
        });
        $(".server_power_startup").click(function () {
            $.get("/server_power/startup");
        });
    });
}

$(document).ready(function() {
    refresh_server_power();
    setInterval(refresh_server_power, 5000);

});
