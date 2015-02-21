var LightControlTimed = function(options) {
  options = options || {};
  options.update_interval = options.update_interval || 1000;
  options.backend_update_interval = options.backend_update_interval || 60 * 60 * 1000;
  var active_days,
      main = $(options.elem),
      update_interval,
      backend_update_interval;
  if (main.length == 0) {
    console.log("!!! Invalid selector for LightControlTimed: " + options.elem);
  }
  var action = main.data("action");

  function onReceiveItemWS(data) {
    updateFields(data);
  }

  function setStartTime(start_time) {
    start_time = start_time.split(":");
    main.find(".start-time-content").html(start_time[0]+":"+start_time[1]);
  }

  function setDuration(duration) {
    duration = parseInt(duration);
    var hours = Math.floor(duration / 3600);
    duration -= hours * 3600;
    var minutes = ("00"+Math.round(duration / 60)).substr(-2);
    main.find(".duration-content").html("+"+hours+":"+minutes);
  }

  function hideItem() {
    $(".timed-lightcontrols-main").find(options.elem).slideUp();
  }

  function showItem() {
    $(".timed-lightcontrols-main").find(options.elem).slideDown();
  }

  function getStartTime() {
    return main.find(".start-time-content").html();
  }

  function getDuration() {
    return main.find(".duration-content").html();
  }

  function getStartTimeMoment() {
    var time = getStartTime().split(":");
    var parsed_time = moment();
    parsed_time.hours(time[0]);
    parsed_time.minutes(time[1]);
    parsed_time.seconds(0);
    return parsed_time;
  }

  function getEndTimeMoment() {
    var start_time = getStartTimeMoment();
    var duration = getDuration().replace("+", "").split(":");
    duration = parseInt(duration[0]) * 3600 + parseInt(duration[1]) * 60;
    return start_time.add(duration, "seconds");
  }

  function getRunning() {
    var icon = main.find(".play-control i");
    if (icon.hasClass("fa-toggle-on")) {
      return true;
    }
    return false;
  }

  function setRunning(status) {
    //TODO: update other components as well
    if (status) {
      // Running
      main.find(".play-control i").removeClass("fa-toggle-off error-message").addClass("fa-toggle-on");
    } else {
      // Stopped
      main.find(".play-control i").removeClass("fa-toggle-on").addClass("fa-toggle-off error-message");
    }
  }

  function updateFields(data) {
    setStartTime(data[0].fields.start_time);
    setDuration(data[0].fields.duration);
    setRunning(data[0].fields.running);
    if (data[0].fields.is_active) {
      showItem();
    } else {
      hideItem();
    }
  }

  function update() {
    $.get("/homecontroller/lightcontrol/timed/get/" + action, function (data) {
      updateFields(data);
    });
  }

  function postUpdate() {
    $.post("/homecontroller/lightcontrol/timed/update/" + action, {start_time: getStartTime(), duration: getDuration(), running: getRunning()}, function(data) {
      updateFields(data);
    });
  }

  function adjustStartTime(dir) {
    // TODO: this is called too early, when data is not loaded yet.
    var start_time = getStartTimeMoment();
    if (dir == "plus") {
      start_time.add(15, "minutes");
    } else {
      start_time.subtract(15, "minutes");
    }
    setStartTime(start_time.format("HH:mm"));
  }

  function updateFromNow() {
    var start_time = getStartTimeMoment(),
        end_time = getEndTimeMoment(),
        now = moment(),
        verb,
        show_progress_indicator,
        content = main.find(".time-left");
    if (now < start_time) { // Not yet started
      verb = "Alkaa";
      show_progress_indicator = false;
      if (!getRunning()) {
        verb = "Alkaisi";
      }
      content.html(verb+" "+start_time.fromNow());
    } else if (now > start_time && now < end_time) { // Currently running
      verb = "Päättyy";
      if (!getRunning()) {
        verb = "Päättyisi";
        show_progress_indicator = false;
      } else {
        show_progress_indicator = true;
      }
      content.html(verb + " " + end_time.fromNow());
    } else {
      // Done for today.
      start_time.add(1, "days");
      verb = "Alkaa";
      show_progress_indicator = false;
      if (!getRunning()) {
        verb = "Alkaisi";
      }
      content.html(verb+" "+start_time.fromNow());
    }
    if (show_progress_indicator == true) {
      main.find(".play-control i").addClass("success-message");
    } else if (show_progress_indicator == false) {
      main.find(".play-control i").removeClass("success-message");
    }
  }

  function adjustDuration(dir) {
    var time = getDuration().replace("+", "").split(":");
    var parsed_time = moment();
    parsed_time.hours(time[0]);
    parsed_time.minutes(time[1]);
    if (dir == "plus") {
      if (parsed_time.hours() < 2) {
        parsed_time.add(15, "minutes");
      }
    } else {
      if ((parsed_time.hours() == 0 && parsed_time.minutes() > 15) || parsed_time.hours() > 0) {
        parsed_time.subtract(15, "minutes");
      }
    }
    main.find(".duration-content").html("+" + parsed_time.format("H:mm"));
  }

  function startInterval() {
    stopInterval();
    updateFromNow();
    update_interval = setInterval(updateFromNow, options.update_interval);
    update();
    backend_update_interval = setInterval(update, options.backend_update_interval);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    if (backend_update_interval) {
      backend_update_interval = clearInterval(backend_update_interval);
    }
  }

  function toggleRunning() {
    if (getRunning()) {
      setRunning(false);
    } else {
      setRunning(true);
    }
  }

  main.find(".duration-time").find(".plus").on("click", function() {
    adjustDuration("plus");
    postUpdate();
  });
  main.find(".duration-time").find(".minus").on("click", function () {
    adjustDuration("minus");
    postUpdate();
  });

  main.find(".start-time").find(".plus").on("click", function() {
    adjustStartTime("plus");
    postUpdate();
  });
  main.find(".start-time").find(".minus").on("click", function() {
    adjustStartTime("minus");
    postUpdate();
  });


  main.find(".play-control").on("click", function() {
    toggleRunning();
    postUpdate();
  });

  ws_generic.register("lightcontrol_timed_" + action, onReceiveItemWS);
  ge_refresh.register("lightcontrol_timed_" + action, update);

  startInterval();

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
  this.hideItem = hideItem;
  this.showItem = showItem;
};


var lightcontrol_timed_evening,
    lightcontrol_timed_morning,
    lightcontrol_timed_weekend_evening,
    lightcontrol_timed_weekend_morning;
$(document).ready(function () {
  lightcontrol_timed_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning"});
  lightcontrol_timed_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening"});
  lightcontrol_timed_weekend_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning-weekend"});
  lightcontrol_timed_weekend_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening-weekend"});
});
