$(document).ready(function () {
  $.each($(".lightcontrol-btn"), function() {
    $(this).data("original-color", $(this).css("background-color"));
    $(this).data("original-classes", $(this).children().attr("class"));

    $(this).on("click", function () {
      var main_elem = $(this);
      if (main_elem.data("running")) {
        return;
      }
      main_elem.data("running", true);
      var command = main_elem.data("command");
      var group = main_elem.data("group") || "0";
      main_elem.animate({backgroundColor: "#ffffff"}, 250);
      main_elem.children().removeClass().addClass("fa fa-spinner fa-spin")
      function animate_success(icon) {
        main_elem.data("running", false);
        main_elem.children().removeClass().addClass("fa fa-"+icon);
        var restore_classes = function () {
          main_elem.children().removeClass().addClass(main_elem.data("original-classes"));
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
