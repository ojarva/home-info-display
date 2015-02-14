var LightControlTimed = function(options) {
  options = options || {}
  options.update_interval = options.update_interval || 1000;
  var main = $(options.elem),
      ws4redis,
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
    } else {
      // Stopped
      main.find(".play-control i").removeClass("fa-stop").addClass("fa-play");
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
    var start_time = getStartTimeMoment();
    if (dir == "plus") {
      start_time.add(15, "minutes");
    } else {
      start_time.subtract(15, "minutes");
    }
    setStartTime(start_time.format("HH:mm"));
  }

  function updateFromNow() {
    var start_time = getStartTimeMoment();
    var end_time = getEndTimeMoment();
    var now = moment();
    var verb;
    var content = main.find(".time-left");
    if (now < start_time) { // Not yet started
      verb = "Alkaa";
      if (!getRunning()) {
        verb = "Alkaisi";
      }
      content.html(verb+" "+start_time.fromNow());
    } else if (now > start_time && now < end_time) { // Currently running
      verb = "Päättyy";
      if (!getRunning()) {
        verb = "Päättyisi";
      }
      content.html(verb+" "+end_time.fromNow());
    } else {
      // Done for today.
      start_time.add(1, "days");
      verb = "Alkaa";
      if (!getRunning()) {
        verb = "Alkaisi";
      }
      content.html(verb+" "+start_time.fromNow());
    }
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

  function startInterval() {
    stopInterval();
    updateFromNow();
    update_interval = setInterval(updateFromNow, options.update_interval);
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
  startInterval();

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};


var lightcontrol_timed_evening,
    lightcontrol_timed_morning;
$(document).ready(function () {
  lightcontrol_timed_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning"});
  lightcontrol_timed_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening"});
});
