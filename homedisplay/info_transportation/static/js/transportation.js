var Transportation = function() {
  var update_interval, timestamp_update_interval;

  function onReceiveItemWS(message) {
    processData(message);
  }

  function clearEntries() {
    $(".transportation ul li").remove();
  }

  function processData(data) {
    clearEntries();
    $.each(data, function() {
      // Loop over stops
      $(".transportation ul").append("<li><i class='fa fa-li fa-2x fa-"+this.icon+"'></i> <span class='line-number'>"+this.line+":</span> <span class='departures' data-minimum-time="+this.minimum_time+"></span></li>");
      var this_departures = $(".transportation ul li .departures").last();
      $.each(this.departures, function () {
        this_departures.append("<span class='auto-update-timestamp' data-timestamp='"+this+"'><span class='minutes'></span><span class='seconds'></span></span> ");
      });
    });
    updateTimestamps();
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

  function update() {
    $.get("/homecontroller/transportation/get_json", function(data) {
      processData(data);
    });
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, 15 * 60 * 1000);
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
  transportation = new Transportation();
  transportation.startInterval();
  // TODO
  $(".main-button-box .birthdays").on("click", function () {
    switchVisibleContent("#birthdays-list-all");
  });
  $("#birthdays-list-all .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
