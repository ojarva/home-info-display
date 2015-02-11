var LightControlTimed = function(options) {
  options = options || {}
  var main = $(options.elem);

  main.find(".play-control").on("click", function() {
    icon = $(this).find("i");
    if (icon.hasClass("fa-stop")) {
      $(this).find("i").removeClass("fa-stop").addClass("fa-play");
    } else {
      $(this).find("i").removeClass("fa-play").addClass("fa-stop");
    }
    updateBackend();
  });

  function updateBackend() {
    // Post all values to backend
    // Parse response and update all fields to current status
  }

  function adjustStartTime(dir) {
    var time = main.find(".start-time-content").html().split(":");
    parsed_time = moment();
    parsed_time.hours(time[0]);
    parsed_time.minutes(time[1]);
    if (dir == "plus") {
      parsed_time.add(15, "minutes");
    } else {
      parsed_time.subtract(15, "minutes");
    }
    main.find(".start-time-content").html(parsed_time.format("HH:mm"));
  }

  function adjustDuration(dir) {
    var time = main.find(".duration-content").html().replace("+", "").split(":");
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
};


var lightcontrol_timed;
$(document).ready(function () {
  lightcontrol_timed = new LightControlTimed({"elem": ".timed-lightcontrol"});
});
