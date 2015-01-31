$(document).ready(function () {
    var lightcontrol_content_file = "/homecontroller/lightcontrol/content";
    if (typeof kitchen != "undefined" && kitchen === true) {
        lightcontrol_content_file += "/kitchen";
    }
    $.get(lightcontrol_content_file, function (data) {
        $("#lightcontrol").html(data);
        $.each($("#lightcontrol .lightcontrol-btn"), function() {
            $(this).bind("click", function () {
                var id = $(this).attr("id").replace("lightcontrol_all_", "");
                $.get("/homecontroller/lightcontrol/control/"+id+"/0");
            });
        });

        $.each($("#lightcontrol .lightcontrol-per-group"), function () {
            $(this).bind("click", function () {
                var classes = $(this).attr("class");
                classes = classes.split(" ");
                var group = classes[1].replace("lightcontrol_", "");
                var command = classes[2].replace("lightcontrol_", "");
                $.get("/homecontroller/lightcontrol/control/"+command+"/"+group);
            });
        });

    });
});
