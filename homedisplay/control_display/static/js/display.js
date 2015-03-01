var ShutdownProgress = function(options) {
  "use strict";
  options = options || {};
  options.timeout = options.timeout || 31000; // in ms
  var update_interval, countdown_start;

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    $("#shutdown-progress .progress-bar").css("width", "0%");
  }

  function stop(source) {
    if (source !== "backend") {
      $.post("/homecontroller/control_display/power/cancel-delayed", function () {
        stopInterval();
        content_switch.switchContent("#main-content");
      });
    } else {
      stopInterval();
      content_switch.switchContent("#main-content");
    }
  }

  function shutdown() {
    $.post("/homecontroller/control_display/power/off");
  }

  function startup() {
    $.post("/homecontroller/control_display/power/on");
  }

  function restartDisplay() {
    $.post("/homecontroller/control_display/restart");
  }

  function update() {
    var time_left = options.timeout - (moment() - countdown_start);
    if (time_left < -15 * 1000) {
      // Something went wrong with the backend
      stop("backend");
    }
    if (time_left < 0) {
      // WS message handles closing the dialog
      return;
    }
    var percent = 100 * (options.timeout - time_left) / options.timeout;
    $("#shutdown-progress .progress-bar").css("width", percent + "%");
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, 100);
  }

  function restart(source) {
    if (source !== "backend") {
      $.post("/homecontroller/control_display/power/delayed-shutdown", function () {
        countdown_start = moment();
        startInterval();
      });
    } else {
      countdown_start = moment();
      startInterval();
    }
  }

  function onReceiveItemWS(message) {
    console.log("Shutdown received", message);
    if (message === "display-off" || message === "display-on" || message === "cancel-delayed") {
      stop("backend");
    } else if (message === "delayed-shutdown") {
      content_switch.switchContent("#shutdown-progress");
      restart("backend");
    }
  }

  ws_generic.register("shutdown", onReceiveItemWS);

  this.restart = restart;
  this.stop = stop;
  this.shutdown = shutdown;
  this.startup = startup;
  this.restartDisplay = restartDisplay;
};

var shutdown_progress;
$(document).ready(function() {
  "use strict";
  shutdown_progress = new ShutdownProgress();
  $("#main-content .close").on("click", function () {
    content_switch.switchContent("#shutdown-progress");
    shutdown_progress.restart();
  });

  $("#shutdown-progress .close, #shutdown-progress .cancel").on("click", function() {
    shutdown_progress.stop();
    content_switch.switchContent("#main-content");
  });
  $("#shutdown-progress .yes").on("click", function() {
    shutdown_progress.shutdown();
  });

  $(".display-power .shutdown-display").on("click", function () {
    shutdown_progress.shutdown();
  });
  $(".display-power .startup-display").on("click", function () {
    shutdown_progress.startup();
  });
  $(".display-power .restart-browser").on("click", function () {
    shutdown_progress.restartDisplay();
  });
});
