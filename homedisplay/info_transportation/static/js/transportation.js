var Transportation = function() {
  "use strict";
  var update_interval, timestamp_update_interval;


  function clearEntries() {
    $(".transportation ul li").remove();
  }


  function updateTimestamps() {
    $(".transportation .auto-update-timestamp").each(function () {
      var diff = moment($(this).data("timestamp")) - moment();
      diff /= 1000;
      if (diff < parseInt($(this).parent().data("minimum-time"))) {
        $(this).fadeOut({duration: 900, complete: function() {
          $(this).remove();
        }});
        return true; // continue
      }
      var minutes_raw = Math.floor(diff / 60);

      var seconds = ("00" + Math.floor(diff - (60 * minutes_raw))).substr(-2, 2);
      $(this).find(".minutes").html(minutes_raw);
      $(this).find(".seconds").html(":" + seconds);
    });
    $(".transportation .departures .seconds").hide();
    $(".transportation .departures").each(function () {
      $(this).find(".auto-update-timestamp").first().addClass("first-departure");
      $(this).find(".seconds").first().show();
    });
  }


  function processData(data) {
    clearEntries();
    $.each(data, function() {
      // Loop over stops
      $(".transportation ul").append("<li><i class='fa fa-li fa-2x fa-" + this.icon + "'></i> <span class='line-number'>" + this.line + ":</span> <span class='departures' data-minimum-time=" + this.minimum_time + "></span></li>");
      var this_departures = $(".transportation ul li .departures").last();
      var departures_for_stop = 0;
      $.each(this.departures, function () {
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
    $.get("/homecontroller/transportation/get_json", function(data) {
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

$(document).ready(function() {
  "use strict";
  transportation = new Transportation();
  transportation.startInterval();
  // TODO
  $(".main-button-box .birthdays").on("click", function () {
    content_switch.switchContent("#birthdays-list-all");
  });
  $("#birthdays-list-all .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
