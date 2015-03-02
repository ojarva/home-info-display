var Transportation = function() {
  "use strict";
  var update_interval, timestamp_update_interval;


  function clearEntries() {
    jq(".transportation ul li").remove();
  }


  function updateTimestamps() {
    jq(".transportation .auto-update-timestamp").each(function () {
      var diff = moment(jq(this).data("timestamp")) - moment();
      diff /= 1000;
      if (diff < parseInt(jq(this).parent().data("minimum-time"))) {
        jq(this).fadeOut({duration: 900, complete: function() {
          jq(this).remove();
        }});
        return true; // continue
      }
      var minutes_raw = Math.floor(diff / 60);

      var seconds = ("00" + Math.floor(diff - (60 * minutes_raw))).substr(-2, 2);
      jq(this).find(".minutes").html(minutes_raw);
      jq(this).find(".seconds").html(":" + seconds);
    });
    jq(".transportation .departures .seconds").hide();
    jq(".transportation .departures").each(function () {
      jq(this).find(".auto-update-timestamp").first().addClass("first-departure");
      jq(this).find(".seconds").first().show();
    });
  }


  function processData(data) {
    clearEntries();
    jq.each(data, function() {
      // Loop over stops
      jq(".transportation ul").append("<li><i class='fa fa-li fa-2x fa-" + this.icon + "'></i> <span class='line-number'>" + this.line + ":</span> <span class='departures' data-minimum-time=" + this.minimum_time + "></span></li>");
      var this_departures = jq(".transportation ul li .departures").last();
      var departures_for_stop = 0;
      jq.each(this.departures, function () {
        this_departures.append("<span class='auto-update-timestamp' data-timestamp='" + this + "'><span class='minutes'></span><span class='seconds'></span></span> ");
        departures_for_stop += 1;
        if (departures_for_stop > 7) {
          return false;
        }
      });
    });
    updateTimestamps();
  }


  function update() {
    jq.get("/homecontroller/transportation/get_json", function(data) {
      processData(data);
    });
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, FAST_UPDATE);
    timestamp_update_interval = setInterval(updateTimestamps, 1000);
    ws_generic.register("public-transportation", processData);
    ge_refresh.register("public-transportation", update);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    if (timestamp_update_interval) {
      timestamp_update_interval = clearInterval(timestamp_update_interval);
    }
    ws_generic.deRegister("public-transportation");
    ge_refresh.deRegister("public-transportation");
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
  this.update = update;
};

var transportation;

jq(document).ready(function() {
  "use strict";
  transportation = new Transportation();
  transportation.startInterval();
  // TODO
  jq(".main-button-box .birthdays").on("click", function () {
    content_switch.switchContent("#birthdays-list-all");
  });
  jq("#birthdays-list-all .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
