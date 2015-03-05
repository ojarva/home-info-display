var ClockCalendar = function (options) {
  options = options || {};
  options.update_interval = options.update_interval || 1000;
  options.sync_interval = options.sync_interval || FAST_UPDATE;
  var update_interval, sync_interval, clock_offset = 0;

  function updateOffset() {
    jq.get("/homecontroller/timer/current_time", function(timestamp) {
      var server_timestamp = parseInt(timestamp);
      clock_offset = -1 * parseInt(new Date(server_timestamp) - new Date()); // In milliseconds
    });
  }

  function getMoment() {
    // Get moment with current offset
    return moment().add(getOffset());
  }

  function getDate() {
    // Get javascript date with current offset
    return (new Date(new Date() + getOffset()));
  }

  function update() {
    var days = new Array("su", "ma", "ti", "ke", "to", "pe", "la");
    var offset_fixed = new Date() - clock_offset;
    var currentTime = new Date(offset_fixed);
    var currentDay = days[currentTime.getDay()];
    var currentDate = currentTime.getDate();
    var currentMonth = currentTime.getMonth()+1;
    jq(".calendar").html(currentDay+" "+currentDate+"."+currentMonth+".");
    var currentHours = currentTime.getHours();
    var currentMinutes = currentTime.getMinutes();
    var currentSeconds = currentTime.getSeconds();
    currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
    currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;
    jq(".clock").html(currentHours+":"+currentMinutes+":"+currentSeconds);
  }

  function getOffset() {
    return clock_offset;
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    if (sync_interval) {
      sync_interval = clearInterval(sync_interval);
    }
  }

  function startInterval() {
    stopInterval();
    update();
    updateOffset();
    update_interval = setInterval(update, options.update_interval);
    sync_interval = setInterval(updateOffset, options.sync_interval);
  }

  ge_refresh.register("clock-sync", updateOffset);

  this.updateOffset = updateOffset;
  this.getOffset = getOffset;
  this.update = update;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
  this.getMoment = getMoment;
  this.getDate = getDate;
};

var TimedRefresh = function() {
  var last_run_on_hour = clock.getDate().getHours(),
      last_run_on_day = clock.getDate().getDay(), // This is not unique, but if delay between checks is more than a month, something is seriously wrong.
      intervals = {};

  function register(key, interval, callback) {
    if (!(interval in intervals)) {
        intervals[interval] = {};
    }
    intervals[interval][key] = callback;
  }

  function deRegister(key, interval) {
    if (interval in intervals) {
      delete intervals[interval][key];
    }
  }

  function executeCallbacks(interval) {
    if (!(interval in internals)) {
      console.warn("Interval ", interval, " does not exist");
      return;
    }
    for (key in intervals[interval]) {
      intervals[interval][key]();
    }
  }

  function runIntervals() {
    var now = clock.getDate();
    var hour = now.getHours(),
        day = now.getDay();
    if (hour != last_run_on_hour) {
      last_run_on_hour = hour;
      executeCallbacks("hourly");
    }
    if (day != last_run_on_day) {
      last_run_on_day = day;
      executeCallbacks("daily");
    }
  }

  // Missing intervals by 5 seconds is not optimal, but good enough.
  setInterval(runIntervals, 5000);

  this.register = register;
  this.deRegister = deRegister;
}

jq(document).ready(function() {
    clock = new ClockCalendar();
    clock.startInterval();
    ge_intervals = new TimedRefresh();
});
