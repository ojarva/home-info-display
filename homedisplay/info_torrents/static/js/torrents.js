var Torrents = function() {
  "use strict";
  var update_interval;


  function clearItems() {
    jq("#torrent-items tr").remove();
  }


  function processData(items) {
    clearItems();
    jq.each(items, function() {
      jq("#torrent-items").append("<tr data-hash='" + this.hash + "'><td>" + this.filename + "</td><td>" + filesize(this.size) + "</td><td>" + this.downloaded_percent + "%</td><td>" + this.up_speed + "</td><td>" + this.eta + "</td><td>" + this.netdisk + "</td><td><div class='action-button animate-click stripe-box' data-action='remove'><i data-original-classes='fa fa-trash' class='fa fa-trash'></i></div> <div class='action-button animate-click stripe-box' data-action='stop'><i data-original-classes='fa fa-stop' class='fa fa-stop'></i></div> <div class='action-button animate-click stripe-box' data-action='play'><i data-original-classes='fa fa-play' class='fa fa-play'></i></div> </td></tr>");
    });
    jq("#torrent-items .action-button").on("click", function () {
      content_switch.userActivity();
      var command = jq(this).data("action");
      var hash = jq(this).parent().parent().data("hash");
      jq(this).find("i").removeClass().addClass("fa fa-spin fa-spinner");
      jq.post("/homecontroller/torrents/action/" + command + "/" + hash, function () {
        // No need to remove spinner, as whole table will be redrawn.
      });
    });
  }


  function update() {
    jq.get("/homecontroller/torrents/list", function(data) {
      processData(data);
    });
  }


  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
  }


  function startInterval() {
    stopInterval();
    update();
    update_interval = startInterval(update, SLOW_UPDATE);
  }


  ws_generic.register("torrent-list", processData);
  ge_refresh.register("torrent-list", update);

  this.update = update;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};
var torrents;

jq(document).ready(function () {
  "use strict";
  torrents = new Torrents();
  jq(".main-button-box .linux-downloads").on("click", function () {
    torrents.update();
    content_switch.switchContent("#linux-downloads-modal");
  });
  jq("#linux-downloads-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
