var ShutdownProgress = function(options) {
  options = options || {};
  options.timeout = options.timeout || 30000; // in ms
  var update_interval, countdown_start;

  function shutdown() {
    stop();
    $.get("/homecontroller/display/control/off");
  }

  function update() {
    var time_left = options.timeout - (moment() - countdown_start);
    if (time_left < 0) {
      shutdown();
      return;
    }
    var percent = 100 * (options.timeout - time_left) / options.timeout;
    $("#shutdown-progress .progress-bar").css("width", percent+"%");
  }

  function onReceiveItemWS(message) {
    console.log("Shutdown received", message);
    if (message == "shutdown_delay") {
      switchVisibleContent("#shutdown-progress");
      restart();
    } else if (message == "shutdown_cancel") {
      switchVisibleContent("#main-content");
      stop();
    }
  }

  function restart() {
    countdown_start = moment();
    startInterval();
  }

  function stop() {
    stopInterval();
    switchVisibleContent("#main-content");
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, 100);

  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    $("#shutdown-progress .progress-bar").css("width", "0%");

  }

  ws_generic.register("shutdown", onReceiveItemWS);

  this.restart = restart;
  this.stop = stop;
  this.shutdown = shutdown;
};

var shutdown_progress;
$(document).ready(function() {
  shutdown_progress = new ShutdownProgress();
  $("#main-content .close").on("click", function () {
    switchVisibleContent("#shutdown-progress");
    shutdown_progress.restart();
  });

  $("#shutdown-progress .close, #shutdown-progress .cancel").on("click", function() {
    shutdown_progress.stop();
    switchVisibleContent("#main-content");
  });
  $("#shutdown-progress .yes").on("click", function() {
    shutdown_progress.shutdown();
  });
});
