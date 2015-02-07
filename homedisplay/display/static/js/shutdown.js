var ShutdownProgress = function(options) {
  options = options || {}
  options.timeout = options.timeout || 30000; // in ms
  var update_interval, countdown_start;

  function shutdown() {
    stop();
    $.get("/homecontroller/display/control/off");
  }

  function update() {
    var time_left = options.timeout - (moment() - countdown_start);
    console.log(time_left - 0);
    if (time_left < 0) {
      shutdown();
      return;
    }
    var percent = 100 * (options.timeout - time_left) / options.timeout;
    $("#shutdown-progress .progress-bar").css("width", percent+"%");
  }

  function onReceiveItemWS(message) {
    console.log("Shutdown received", message);
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
    ws4redis = new WS4Redis({
      uri: websocket_root+'shutdown?subscribe-broadcast&publish-broadcast&echo',
      receive_message: onReceiveItemWS,
      heartbeat_msg: "--heartbeat--"
    });
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    try {
      ws4redis.close();
    } catch(e) {

    }
    $("#shutdown-progress .progress-bar").css("width", "0%");

  }
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
    switchVisibleContent("#main-content");
  });
  $("#shutdown-progress .yes").on("click", function() {
    shutdown_progress.shutdown();
  })

});
