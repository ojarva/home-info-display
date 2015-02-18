var ServerPower = function(options) {
  options = options || {};
  options.update_interval = options.update_interval || 10 * 60 * 1000;
  var main_elem = $(options.main_elem);
  var interval;

  function showButton(button_name) {
    main_elem.find(".action-button").not("." + button_name).slideUp();
    main_elem.find("." + button_name).slideDown();
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
    setStatus(message);
  }

  function startInterval() {
    stopInterval();
    refreshServerPower();
    interval = setInterval(refreshServerPower, options.update_interval);
    ws_generic.register("server_power", onReceiveItemWS);
  }

  function stopInterval() {
    if (interval) {
      interval = clearInterval(interval);
    }
    ws_generic.deRegister("server_power");
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
  server_power = new ServerPower({main_elem: ".server-power"});
  server_power.startInterval();
});
