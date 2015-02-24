var Torrents = function() {
  var update_interval;

  function clearItems() {
    $("#torrent-items tr").remove();
  }

  function processData(items) {
    clearItems();
    $.each(items, function() {
      $("#torrent-items").append("<tr data-hash='"+this.hash+"'><td>"+this.filename+"</td><td>"+filesize(this.size)+"</td><td>"+this.downloaded_percent+"%</td><td>"+this.up_speed+"</td><td>"+this.eta+"</td><td>"+this.netdisk+"</td><td><div class='action-button animate-click stripe-box' data-action='remove'><i data-original-classes='fa fa-trash' class='fa fa-trash'></i></div> <div class='action-button animate-click stripe-box' data-action='stop'><i data-original-classes='fa fa-stop' class='fa fa-stop'></i></div> <div class='action-button animate-click stripe-box' data-action='play'><i data-original-classes='fa fa-play' class='fa fa-play'></i></div> </td></tr>")
    });
    $("#torrent-items .action-button").on("click", function () {
      var command = $(this).data("action");
      var hash = $(this).parent().parent().data("hash");
      $(this).find("i").removeClass().addClass("fa fa-spin fa-spinner");
      $.post("/homecontroller/torrents/action/"+command+"/"+hash, function () {
        // No need to remove spinner, as whole table will be redrawn.
      });
    });
  }


  function update() {
    $.get("/homecontroller/torrents/list", function(data) {
      processData(items);
    })
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = startInterval(update, 60 * 60 * 1000);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
  }

  ws_generic.register("torrent-list", processData);
  ge_refresh.register("torrent-list", update);

  this.update = update;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};
var torrents;

$(document).ready(function () {
  torrents = new Torrents();
  $(".main-button-box .linux-downloads").on("click", function () {
    torrents.update();
    switchVisibleContent("#linux-downloads-modal");
  });
  $("#linux-downloads-modal .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
