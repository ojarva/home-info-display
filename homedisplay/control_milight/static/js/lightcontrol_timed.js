var LightControlTimed = function(options) {
  // TODO: this should be refactored to use latest_data.start_datetime and .end_datetime instead of parsing from html.
  options = options || {};
  options.update_interval = options.update_interval || 1000;
  options.backend_update_interval = options.backend_update_interval || 60 * 60 * 1000;
  var active_days,
      main = $(options.elem),
      update_interval,
      backend_update_interval,
      latest_data,
      running;
  if (main.length == 0) {
    console.warn("!!! Invalid selector for LightControlTimed: " + options.elem);
  }
  var action = main.data("action");

  function getNextStartDatetime() {
    if (latest_data && latest_data.fields) {
      return moment(latest_data.fields.start_datetime);
    }
  }
  function getNextEndDatetime() {
    if (latest_data && latest_data.fields) {
      return moment(latest_data.fields.end_datetime);
    }
  }

  function pauseOverride() {
    main.find(".play-pause-control").slideDown();
  }

  function resumeOverride(source) {
    main.find(".play-pause-control").slideUp();
    if (source == "ui") {
      $.post("/homecontroller/lightcontrol/timed/override-resume/"+ action);
    }
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

  function getDurationSeconds() {
    var duration = getDuration().replace("+", "").split(":");
    duration = parseInt(duration[0]) * 3600 + parseInt(duration[1]) * 60;
    return duration;
  }

  function getStartTimeMoment() {
    var time = getStartTime().split(":");
    var parsed_time = moment();
    parsed_time.hours(time[0]);
    parsed_time.minutes(time[1]);
    parsed_time.seconds(0);
    return parsed_time;
  }


  function setRunning(status) {
    running = status;
    if (running) {
      main.find(".play-control i").removeClass("fa-toggle-off error-message").addClass("fa-toggle-on");
    } else {
      main.find(".play-control i").removeClass("fa-toggle-on").addClass("fa-toggle-off error-message");
    }
  }

  function updateFields(data) {
    latest_data = data[0];
    setStartTime(data[0].fields.start_time);
    setDuration(data[0].fields.duration);
    setRunning(data[0].fields.running);
    if (data[0].fields.is_overridden) {
      pauseOverride();
    } else {
      resumeOverride("backend");
    }
    lightcontrol_timed_sort.sortTimers();
  }

  function update() {
    $.get("/homecontroller/lightcontrol/timed/get/" + action, function (data) {
      updateFields(data);
    });
  }

  function postUpdate() {
    $.post("/homecontroller/lightcontrol/timed/update/" + action, {start_time: getStartTime(), duration: getDuration(), running: running}, function(data) {
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
    postUpdate();
  }

  function updateFromNow() {
    if (!latest_data) {
      return;
    }
    data = latest_data.fields;
    var start_time = getNextStartDatetime(),
        end_time = getNextEndDatetime(),
        now = moment(),
        verb,
        show_progress_indicator,
        content = main.find(".time-left");
    if (now < end_time && end_time - now < getDurationSeconds() * 1000) { // Currently running
      verb = "päättyy";
      if (!running) {
        verb = "päättyisi";
        show_progress_indicator = false;
      } else {
        show_progress_indicator = true;
      }
      content.html(verb + " " + end_time.fromNow());
    } else if (now < start_time) { // Not yet started
      verb = "alkaa";
      show_progress_indicator = false;
      if (!running) {
        verb = "alkaisi";
      }
      content.html(verb+" "+start_time.fromNow());
    } else {
      // Done for today.
      start_time.add(1, "days");
      verb = "alkaa";
      show_progress_indicator = false;
      if (!running) {
        verb = "alkaisi";
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
    postUpdate();
  }

  function onReceiveItemUpdate(data) {
    updateFields(data);
  }

  function onReceiveOverride(data) {
    if (data.action == "resume") {
      resumeOverride("backend");
    } else {
      pauseOverride();
    }
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

  main.find(".duration-time").find(".plus").on("click", function() {
    content_switch.userAction();
    adjustDuration("plus");
  });
  main.find(".duration-time").find(".minus").on("click", function () {
    content_switch.userAction();
    adjustDuration("minus");
  });

  main.find(".start-time").find(".plus").on("click", function() {
    content_switch.userAction();
    adjustStartTime("plus");
  });
  main.find(".start-time").find(".minus").on("click", function() {
    content_switch.userAction();
    adjustStartTime("minus");
  });


  main.find(".play-control").on("click", function() {
    content_switch.userAction();
    setRunning(!running);
    postUpdate();
  });

  main.find(".play-pause-control").on("click", function () {
    content_switch.userAction();
    resumeOverride("ui");
  });

  ws_generic.multiRegister("lightcontrol_timed_override", "lightcontrol_timed_override_"+ action, onReceiveOverride);
  ws_generic.register("lightcontrol_timed_" + action, onReceiveItemUpdate);
  ge_refresh.register("lightcontrol_timed_" + action, update);

  startInterval();

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
  this.hideItem = hideItem;
  this.showItem = showItem;
  this.getNextStartDatetime = getNextStartDatetime;
  this.getNextEndDatetime = getNextEndDatetime;
};

var ShowTimers = function() {
  function sortTimers() {
    lightcontrol_timed.sort(function (a, b) {
      return a.getNextStartDatetime() - b.getNextStartDatetime();
    });
    lightcontrol_timed[2].hideItem();
    lightcontrol_timed[3].hideItem();
    lightcontrol_timed[0].showItem();
    lightcontrol_timed[1].showItem();
  }

  this.sortTimers = sortTimers;
};

var lightcontrol_timed_evening,
    lightcontrol_timed_morning,
    lightcontrol_timed_weekend_evening,
    lightcontrol_timed_weekend_morning,
    lightcontrol_timed_sort;
var lightcontrol_timed;

$(document).ready(function () {
  lightcontrol_timed_sort = new ShowTimers();
  lightcontrol_timed_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning"});
  lightcontrol_timed_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening"});
  lightcontrol_timed_weekend_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning-weekend"});
  lightcontrol_timed_weekend_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening-weekend"});
  lightcontrol_timed = [lightcontrol_timed_evening, lightcontrol_timed_morning, lightcontrol_timed_weekend_evening, lightcontrol_timed_weekend_morning];

});
