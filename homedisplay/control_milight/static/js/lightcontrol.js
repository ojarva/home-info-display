var LightSlider = function (elem) {
  var this_elem = jq(elem),
      group_id = this_elem.data("id"),
      value = 0,
      update_timeout;

  function updateBackend() {
    if (value > 95) {
      value = 100;
      this_elem.slider("value", value);
    }

    jq.post("/homecontroller/lightcontrol/control/brightness/" + group_id + "/" + value);
  }

  var slider = this_elem.slider({
    value: 0,
    min: 0,
    max: 100,
    range: "max",
    slide: function( event, ui ) {
      if (update_timeout) {
        update_timeout = clearTimeout(update_timeout);
      }
      update_timeout = setTimeout(updateBackend, 100);
      value = ui.value;
    }
  });

};

var LightControl = function () {
  "use strict";

  var color_map = {"white": "valkoinen",
                   "red": "punainen",
                   "blue": "sininen"},
       latest_data,
       delayed_process;

  function initialize(selector) {
    jq.each(jq(".brightness-slider"), function() {
      LightSlider(this);
    });
    jq.each(jq(selector), function() {
      jq(this).data("original-color", jq(this).css("background-color"));
      jq(this).children().not(".active-mode").each(function () {
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
        main_elem.children().not(".active-mode").removeClass().addClass("fa fa-spinner fa-spin");
        function animate_completed(icon) {
          main_elem.data("running", false);
          main_elem.children().not(".active-mode").removeClass().addClass("fa fa-" + icon);
          var restore_classes = function () {
            main_elem.children().not(".active-mode").each(function() {
              var elem = jq(this);
              elem.removeClass().addClass(elem.data("original-classes"));
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

  function delayedProcessData() {
    var max_brightness = 0;
    var data = latest_data;
    if (data && data.groups) {
      jq.each(data.groups, function () {
        var group_id = this.fields.group_id;
        var color = this.fields.color;
        jq(".light-group-" + group_id + "-name").html(this.fields.description);
        jq(".light-group-" + group_id + "-brightness").html(this.fields.current_brightness + "%").data("brightness", this.fields.current_brightness);

        jq(".brightness-slider-group-" + group_id).slider("value", this.fields.current_brightness);
        jq(".brightness-slider-group-" + group_id).css("background-color", color);

        var color_elem = jq(".light-group-" + group_id + "-color");
        if (color in color_map) {
          color_elem.html(color_map[color]);
        }
        color_elem.data(color);
        jq(".light-group-" + group_id + "-on").data(this.fields.on);
        if (this.fields.on) {
          jq(".light-group-" + group_id + "-on").html("<i class='fa fa-toggle-on'></i>");
        } else {
          jq(".light-group-" + group_id + "-on").html("<i class='fa fa-toggle-off'></i>");
        }
        max_brightness = Math.max(max_brightness, this.fields.morning_light_level);

        if (this.fields.morning_light_level < 10) {
          jq(".lights-morning-auto-" + group_id).addClass("lights-morning-dim").removeClass("lights-morning-bright");
        } else {
          jq(".lights-morning-auto-" + group_id).addClass("lights-morning-bright").removeClass("lights-morning-dim");
        }
      });
      if (max_brightness < 10) {
        jq(".lights-morning-auto").addClass("lights-morning-dim").removeClass("lights-morning-bright");
      } else {
        jq(".lights-morning-auto").addClass("lights-morning-bright").removeClass("lights-morning-dim");
      }
    }
    if (data && data.main_buttons) {
      jq.each(data.main_buttons, function(key, value) {
        if (value) {
          jq(".lights-" + key).find(".active-mode").show();
        } else {
          jq(".lights-" + key).find(".active-mode").hide();
        }
      });
    }
  }

  function processData(data) {
    // Usually there is multiple updates for this. Delay processing a bit.
    latest_data = data;
    if (delayed_process) {
      delayed_process = clearTimeout(delayed_process);
    }
    delayed_process = setTimeout(delayedProcessData, 100);
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
