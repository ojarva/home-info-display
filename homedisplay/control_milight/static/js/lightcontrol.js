$(document).ready(function () {
    $.get("/lightcontrol/content", function (data) {
        $("#lightcontrol").html(data);
        $.each($("#lightcontrol .lightcontrol-btn"), function() {
            $(this).bind("click", function () {
                var id = $(this).attr("id").replace("lightcontrol_all_", "");
                $.get("/lightcontrol/control/"+id+"/0");
            });
        });

        $.each($("#lightcontrol .lightcontrol-btn-mini"), function () {
            $(this).bind("click", function () {
                var classes = $(this).attr("class");
                classes = classes.split(" ");
                var group = classes[1].replace("lightcontrol_", "");
                var command = classes[2].replace("lightcontrol_", "");
                $.get("/lightcontrol/control/"+command+"/"+group);
            });
        });

    });
});
