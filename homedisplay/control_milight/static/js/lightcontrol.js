var LightControl = function() {

  function initialize(selector) {
    $.each($(selector), function() {
      $(this).data("original-color", $(this).css("background-color"));
      $(this).children().each(function () {
        $(this).data("original-classes", $(this).attr("class"));
      });

      $(this).on("click", function () {
        var main_elem = $(this), command, group, source;
        if (main_elem.data("running")) {
          return;
        }
        main_elem.data("running", true);
        command = main_elem.data("command");
        group = main_elem.data("group") || "0";
        source = main_elem.data("source");
        main_elem.animate({backgroundColor: "#ffffff"}, 250);
        main_elem.children().removeClass().addClass("fa fa-spinner fa-spin");
        function animate_completed(icon) {
          main_elem.data("running", false);
          main_elem.children().removeClass().addClass("fa fa-" + icon);
          var restore_classes = function () {
            main_elem.children().each(function() {
              $(this).removeClass().addClass($(this).data("original-classes"));
            });
            main_elem.stop().animate({backgroundColor: main_elem.data("original-color")}, 1000);
          };
          setTimeout(restore_classes, 2000);
        }

        var url = "/homecontroller/lightcontrol/control/";
        if (source) {
          url += "source/" + source + "/" + command;
        } else {
          url += command + "/" + group;
        }

        $.ajax({
          url: url,
          success: function () {
            animate_completed("check");
          },
          error: function () {
            animate_completed("times");
          }
        });
      });
    });
  }

  this.initialize = initialize;
};

var light_control;
$(document).ready(function () {
  light_control = new LightControl();
  light_control.initialize(".lightcontrol-btn");

  $(".main-button-box .lights").on("click", function() {
    switchVisibleContent("#lightcontrol-modal");
  });
  $("#lightcontrol-modal .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
