var MomentAutoUpdate = function(options) {
  options = options || {};
  options.update_interval = options.update_interval || 15000;
  options.selector = options.selector || ".auto-fromnow-update"

  var update_interval;
  function update() {
    var elem = $(options.selector);
    $.each(elem, function () {
      var ts = $(this).data("timestamp");
      $(this).html(moment(ts).fromNow());
    });
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, options.update_interval);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
  this.update = update;
};

var moment_auto_update;
$(document).ready(function() {
  moment_auto_update = new MomentAutoUpdate();
  moment_auto_update.startInterval();
});
