function load_repeating_tasks() {
    $.get("/homecontroller/repeating_tasks/status", function(data) {
        $("#repeating_tasks .list-group").html(data);
        $("#repeating_tasks .list-group-item").each(function() {
            $(this).click(function() {
                var id = $(this).data("id");
                $.get("/homecontroller/repeating_tasks/done/"+id, function() {
                    load_repeating_tasks();
                });
                return false;
            });
        });
    });
}
$(document).ready(function () {
    $.get("/homecontroller/repeating_tasks/content", function (data) {
        $("#repeating_tasks").html(data);
        load_repeating_tasks();
        setInterval(load_repeating_tasks, 60000)
    });
});
