var LightControl = function() {
  "use strict";

  var color_map = {"white": "valkoinen",
                   "red": "punainen",
                   "blue": "sininen"};

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
          type: "POST",
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

  function processData(data) {
    console.log("processData", data);
    jq.each(data, function () {
      var group_id = this.fields.group_id;
      jq(".light-group-"+group_id+"-name").html(this.fields.description);
      jq(".light-group-"+group_id+"-brightness").html(this.fields.current_brightness+"%").data("brightness", this.fields.current_brightness);
      var color = this.fields.color;
      var color_elem = jq(".light-group-"+group_id+"-color");
      if (color in color_map) {
        color_elem.html(color_map[color]);
      }
      color_elem.data(color);
      jq(".light-group-"+group_id+"-on").data(this.fields.on);
      if (this.fields.on) {
        jq(".light-group-"+group_id+"-on").html("<i class='fa fa-toggle-on'></i>");
      } else {
        jq(".light-group-"+group_id+"-on").html("<i class='fa fa-toggle-off'></i>");
      }
    });
  }

  function update() {
    jq.get("/homecontroller/lightcontrol/status", function(data) {
      processData(data);
    });
  }

  ws_generic.register("lightcontrol", processData);
  ge_refresh.register("lightcontrol", update);
  this.initialize = initialize;
  this.update = update;
};

var light_control;
jq(document).ready(function () {
  "use strict";
  light_control = new LightControl();
  light_control.initialize(".lightcontrol-btn");
  light_control.update();

  jq(".main-button-box .lights").on("click", function() {
    content_switch.switchContent("#lightcontrol-modal");
  });
  jq("#lightcontrol-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
