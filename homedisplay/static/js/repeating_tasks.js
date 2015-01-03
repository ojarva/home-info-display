$(document).ready(function () {
    $.get("/repeating_tasks/content", function (data) {
        $("#repeating_tasks").html(data);
    })
});
