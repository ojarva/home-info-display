var LightControl = function() {
  "use strict";

  function initialize(selector) {
    jq.each(jq(selector), function() {
      jq(this).data("original-color", jq(this).css("background-color"));
      jq(this).children().each(function () {
        jq(this).data("original-classes", jq(this).attr("class"));
      });

      jq(this).on("click", function () {
        content_switch.userAction();
        var main_elem = jq(this), command, group, source;
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
              jq(this).removeClass().addClass(jq(this).data("original-classes"));
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

        jq.ajax({
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
jq(document).ready(function () {
  "use strict";
  light_control = new LightControl();
  light_control.initialize(".lightcontrol-btn");

  jq(".main-button-box .lights").on("click", function() {
    content_switch.switchContent("#lightcontrol-modal");
  });
  jq("#lightcontrol-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
