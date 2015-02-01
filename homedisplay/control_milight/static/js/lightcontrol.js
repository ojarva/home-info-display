$(document).ready(function () {
  $.each($(".lightcontrol-btn"), function() {
    $(this).data("original-color", $(this).css("background-color"));
    $(this).on("click", function () {
        var main_elem = $(this);
        var original_classes = main_elem.children().attr("class");
        var command = main_elem.data("command");
        var group = main_elem.data("group") || "0";
        main_elem.animate({backgroundColor: "#ffffff"}, 250);
        main_elem.children().removeClass().addClass("fa fa-spinner fa-spin")
        function animate_success(icon) {
          main_elem.children().removeClass().addClass("fa fa-"+icon);
          var restore_classes = function () {
            main_elem.children().removeClass().addClass(original_classes);
            main_elem.stop().animate({backgroundColor: main_elem.data("original-color")}, 1000);
          }
          setTimeout(restore_classes, 2000);
        }

        $.ajax({
          url: "/homecontroller/lightcontrol/control/"+command+"/"+group,
          success: function () {
            animate_success("check");
          },
          error: function () {
            animate_success("times");
          }
        });
      });
  });
});
