var DoorScreensaver = function () {
  var last_activity = new Date(),
      hide_interval,
      timeout = 2 * 60 * 1000;

  function startScreensaver() {
    jq(".screensaver").slideDown();
  }

  function activity() {
    jq(".screensaver").fadeOut("fast");
    last_activity = new Date();
  }

  function update() {
    var now = clock.getDate();
    var hour = now.getHours();
    if (hour > 21 || hour < 8) {
      // Active
      if (new Date() - last_activity > timeout) {
        startScreensaver();
      }
    } else {
      activity();
    }
  }

  hide_interval = setInterval(update, 60 * 1000);

  jq("body").on("click", function () {
    activity();
  });

};


var door_screensaver;
jq(document).ready(function () {
  door_screensaver = new DoorScreensaver();
  var height = jq(window).height();
  jq(".content-box").css("height", height).css("min-height", height);
});
