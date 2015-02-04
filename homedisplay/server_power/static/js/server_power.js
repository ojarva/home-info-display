var ServerPower = function() {
  var interval;
  var main_elem = $("#server_power");

  function showButton(button_name) {
    main_elem.find(".action-button").hide();
    main_elem.find("."+button_name).show();
  }
  function refreshServerPower() {
    $.get("/homecontroller/server_power/status", function (data) {
      if (data.status == "down") {
        showButton("startup");
      } else if (data.status == "not_responding") {
        showButton("unknown");
      } else if (data.status == "running") {
        showButton("shutdown");
      }
    });
  }

  function startInterval() {
    stopInterval();
    refreshServerPower();
    interval = setInterval(refreshServerPower, 5000);
  }

  function stopInterval() {
    if (interval) {
      interval = clearInterval(interval);
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
