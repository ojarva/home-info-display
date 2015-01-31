$(document).ready(function () {
  $.each($(".lightcontrol-btn"), function() {
      $(this).on("click", function () {
        var command = $(this).data("command");
        var group = $(this).data("group") || "0";
        $.get("/homecontroller/lightcontrol/control/"+command+"/"+group);
      });
  });
});
