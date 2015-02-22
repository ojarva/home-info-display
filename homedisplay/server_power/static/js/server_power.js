var ServerPower = function(options) {
  options = options || {};
  options.update_interval = options.update_interval || 10 * 60 * 1000;
  var main_elem = $(options.main_elem),
      interval,
      spinner_until_status_from,
      button_in_progress_timeout;

  function showButton(button_name) {
    main_elem.find(".action-button").not("." + button_name).slideUp();
    main_elem.find("." + button_name).slideDown();
  }

  function setStatus(data) {
    if (data.in_progress) {
      if (spinner_until_status_from) {
        // Waiting for status change
        if (data.in_progress != spinner_until_status_from) {
          // Status changed
          removeSpinners();
        }
      } else {
        // Should wait for status change
        spinner_until_status_from = data.in_progress;
        setSpinners();
      }
    }
    if (data.status == "down") {
      showButton("startup");
    } else if (data.status == "not_responding") {
      showButton("unknown");
    } else if (data.status == "running") {
      showButton("shutdown");
    }

  }
  function refreshServerPower() {
    $.get("/homecontroller/server_power/status", function (data) {
      setStatus(data);
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

  function removeSpinners() {
    spinner_until_status_from = null;
    main_elem.find(".action-button i").each(function () {
      $(this).removeClass().addClass($(this).data("original-classes"));
    });
    if (button_in_progress_timeout) {
      button_in_progress_timeout = clearTimeout(button_in_progress_timeout);
    }
  }

  function setSpinners() {
    main_elem.find(".action-button i").removeClass().addClass("fa fa-spinner fa-spin");
    // If status does not change, remove spinner.
    button_in_progress_timeout = setTimeout(removeSpinners, 60 * 1000);
  }

  main_elem.find(".action-button i").each(function () {
    $(this).data("original-classes", $(this).attr("class"));
  })

  main_elem.find(".startup").on("click", function() {
    spinner_until_status_from = "down";
    setSpinners();
    $.post("/homecontroller/server_power/startup", function () {
    });
  });

  main_elem.find(".shutdown").on("click", function() {
    spinner_until_status_from = "running";
    setSpinners();
    $.post("/homecontroller/server_power/shutdown", function () {
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
