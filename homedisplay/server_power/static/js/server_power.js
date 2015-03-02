var ServerPower = function(options) {
  "use strict";
  options = options || {};
  options.update_interval = options.update_interval || FAST_UPDATE;
  var main_elem = jq(options.main_elem),
      interval,
      spinner_until_status_from,
      button_in_progress_timeout;


  function removeSpinners() {
    spinner_until_status_from = null;
    main_elem.find(".action-button i").each(function () {
      jq(this).removeClass().addClass(jq(this).data("original-classes"));
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


  function showButton(button_name) {
    main_elem.find(".action-button").not("." + button_name).hide();
    main_elem.find("." + button_name).show();
  }


  function setStatus(data) {
    if (data.in_progress) {
      if (spinner_until_status_from) {
        // Waiting for status change
        if (data.in_progress !== spinner_until_status_from) {
          // Status changed
          removeSpinners();
        }
      } else {
        // Should wait for status change
        spinner_until_status_from = data.in_progress;
        setSpinners();
      }
    }
    if (data.status === "down") {
      showButton("startup");
    } else if (data.status === "not_responding") {
      showButton("unknown");
    } else if (data.status === "running") {
      showButton("shutdown");
    }
  }


  function refreshServerPower() {
    jq.get("/homecontroller/server_power/status", function (data) {
      setStatus(data);
    });
  }


  function onReceiveItemWS(message) {
    setStatus(message);
  }


  function stopInterval() {
    if (interval) {
      interval = clearInterval(interval);
    }
    ws_generic.deRegister("server_power");
  }


  function startInterval() {
    stopInterval();
    refreshServerPower();
    interval = setInterval(refreshServerPower, options.update_interval);
    ws_generic.register("server_power", onReceiveItemWS);
  }


  main_elem.find(".action-button i").each(function () {
    jq(this).data("original-classes", jq(this).attr("class"));
  });

  main_elem.find(".startup").on("click", function() {
    spinner_until_status_from = "down";
    setSpinners();
    jq.post("/homecontroller/server_power/startup", function () {
    });
  });

  main_elem.find(".shutdown").on("click", function() {
    spinner_until_status_from = "running";
    setSpinners();
    jq.post("/homecontroller/server_power/shutdown", function () {
    });
  });


  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var server_power;

jq(document).ready(function() {
  "use strict";
  server_power = new ServerPower({main_elem: ".server-power"});
  server_power.startInterval();
});
