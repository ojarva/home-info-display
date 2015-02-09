var ServerPower = function() {
  var interval, ws4redis;
  var main_elem = $("#server_power");

  function showButton(button_name) {
    main_elem.find(".action-button").hide();
    main_elem.find("."+button_name).show();
  }

  function setStatus(status) {
    if (status == "down") {
      showButton("startup");
    } else if (status == "not_responding") {
      showButton("unknown");
    } else if (status == "running") {
      showButton("shutdown");
    }

  }
  function refreshServerPower() {
    $.get("/homecontroller/server_power/status", function (data) {
      setStatus(data.status);
    });
  }

  function onReceiveItemWS(message) {
    console.log("server_power: backend requests update");
    setStatus(message);
  }

  function startInterval() {
    stopInterval();
    refreshServerPower();
    interval = setInterval(refreshServerPower, 60 * 1000);
    ws4redis = new WS4Redis({
      uri: websocket_root+'server_power?subscribe-broadcast&publish-broadcast&echo',
      receive_message: onReceiveItemWS,
      heartbeat_msg: "--heartbeat--"
    });
  }

  function stopInterval() {
    if (interval) {
      interval = clearInterval(interval);
    }
    try {
      ws4redis.close();
    } catch(e) {
    }
  }

  main_elem.find(".startup").on("click", function() {
    $.get("/homecontroller/server_power/startup", function () {
    });
  });

  main_elem.find(".shutdown").on("click", function() {
    $.get("/homecontroller/server_power/shutdown", function () {
    });
  });


  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var server_power;

$(document).ready(function() {
  server_power = new ServerPower();
  server_power.startInterval();
});
