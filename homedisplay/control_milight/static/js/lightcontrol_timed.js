var LightControlTimed = function(options) {
  options = options || {}
  options.update_interval = options.update_interval || 1000;
  var main = $(options.elem),
      ws4redis, // TODO: start ws4redis
      action = main.data("action"),
      update_interval;

  function onReceiveItemWS(message) {
    update();
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

  function getStartTime() {
    return main.find(".start-time-content").html();
  }

  function getDuration() {
    return main.find(".duration-content").html();
  }

  function getRunning() {
    icon = main.find(".play-control i");
    if (icon.hasClass("fa-stop")) {
      return true;
    }
    return false;
  }

  function setRunning(status) {
    //TODO: update other components as well
    if (status) {
      // Running
      main.find(".play-control i").removeClass("fa-play").addClass("fa-stop");
      startInterval();
    } else {
      // Stopped
      main.find(".play-control i").removeClass("fa-stop").addClass("fa-play");
      stopInterval();
    }
  }

  function update() {
    $.get("/homecontroller/lightcontrol/timed/get/"+ action, function (data) {
      setStartTime(data[0].fields.start_time);
      setDuration(data[0].fields.duration);
      setRunning(data[0].fields.running);
    });
  }

  function updateBackend() {
    $.post("/homecontroller/lightcontrol/timed/update/" + action, {start_time: getStartTime(), duration: getDuration(), running: getRunning()}, function(data) {
      setStartTime(data[0].fields.start_time);
      setDuration(data[0].fields.duration);
      setRunning(data[0].fields.running);
    });
  }

  function adjustStartTime(dir) {
    var time = getStartTime().split(":");
    parsed_time = moment();
    parsed_time.hours(time[0]);
    parsed_time.minutes(time[1]);
    if (dir == "plus") {
      parsed_time.add(15, "minutes");
    } else {
      parsed_time.subtract(15, "minutes");
    }
    setStartTime(parsed_time.format("HH:mm"));
  }

  function adjustDuration(dir) {
    var time = getDuration().replace("+", "").split(":");
    parsed_time = moment();
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
    main.find(".duration-content").html("+"+parsed_time.format("H:mm"));
  }

  function setPercent(percent) {
    main.find(".fading-progress .progress-bar").css("width", percent+"%");
  }

  function updateCounter() {
    var time = getStartTime().split(":");
    parsed_time = moment();
    parsed_time.hours(time[0]);
    parsed_time.minutes(time[1]);
    parsed_time.seconds(0);
    var duration = getDuration().replace("+", "").split(":");
    var duration_seconds = parseInt(duration[0]) * 3600 + parseInt(duration[1]) * 60;
    var end_time = moment(parsed_time).add(duration_seconds, "seconds");
    var time_diff = (moment() - parsed_time) / 1000;
    if (time_diff < duration_seconds) {
      setPercent(time_diff / duration_seconds * 100);
      main.find(".time-left-container").slideDown();
      main.find(".time-left").data("timestamp", end_time);
      main.find(".time-left").html(end_time.fromNow());
    } else {
      main.find(".time-left-container").slideUp();
    }
  }

  function startInterval() {
    stopInterval();
    updateCounter();
    update_interval = setInterval(updateCounter, options.update_interval);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
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
    updateBackend();
  });
  main.find(".duration-time").find(".minus").on("click", function () {
    adjustDuration("minus");
    updateBackend();
  });

  main.find(".start-time").find(".plus").on("click", function() {
    adjustStartTime("plus");
    updateBackend();
  });
  main.find(".start-time").find(".minus").on("click", function() {
    adjustStartTime("minus");
    updateBackend();
  });


  main.find(".play-control").on("click", function() {
    toggleRunning();
    updateBackend();
  });

  ws4redis = new WS4Redis({
    uri: websocket_root+'lightcontrol_timed?subscribe-broadcast&publish-broadcast&echo',
    receive_message: onReceiveItemWS,
    heartbeat_msg: "--heartbeat--"
  });

  update();

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};


var lightcontrol_timed_evening,
    lightcontrol_timed_morning;
$(document).ready(function () {
  lightcontrol_timed_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning"});
  lightcontrol_timed_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening"});
});
