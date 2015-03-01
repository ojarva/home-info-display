var ClockCalendar = function (options) {
  options = options || {};
  options.update_interval = options.update_interval || 1000;
  options.sync_interval = options.sync_interval || FAST_UPDATE;
  var update_interval, sync_interval, clock_offset = 0;

  function updateOffset() {
    $.get("/homecontroller/timer/current_time", function(timestamp) {
      var server_timestamp = parseInt(timestamp) + 7200000; // TODO: static value
      clock_offset = -1 * parseInt(new Date(server_timestamp) - new Date());
    });
  }

  function update() {
    var days = new Array("su", "ma", "ti", "ke", "to", "pe", "la");
    var offset_fixed = new Date() - clock_offset;
    var currentTime = new Date(offset_fixed);
    var currentDay = days[currentTime.getDay()];
    var currentDate = currentTime.getDate();
    var currentMonth = currentTime.getMonth()+1;
    $(".calendar").html(currentDay+" "+currentDate+"."+currentMonth+".");
    var currentHours = currentTime.getHours();
    var currentMinutes = currentTime.getMinutes();
    var currentSeconds = currentTime.getSeconds();
    currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
    currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;
    $(".clock").html(currentHours+":"+currentMinutes+":"+currentSeconds);
  }

  function getOffset() {
    return clock_offset;
  }

  function startInterval() {
    stopInterval();
    update();
    updateOffset();
    update_interval = setInterval(update, options.update_interval);
    sync_interval = setInterval(updateOffset, options.sync_interval);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    if (sync_interval) {
      sync_interval = clearInterval(sync_interval);
    }
  }

  this.updateOffset = updateOffset;
  this.getOffset = getOffset;
  this.update = update;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var clock_calendar_handler;

$(document).ready(function() {
    clock_calendar_handler = new ClockCalendar();
    clock_calendar_handler.startInterval();
});
