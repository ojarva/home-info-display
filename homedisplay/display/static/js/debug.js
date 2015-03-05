var Debug = function () {
  var elem = jq("#debug-modal .debug-list");

  function addItem(text, itemClass) {
    now = clock.getMoment();
    elem.prepend("<li><i class='" + itemClass + " fa fa-fw fa-li fa-bug'></i> " + now.format("HH:mm:ss") + " " + text + " (<span class='auto-fromnow-update' data-timestamp='" + now + "'>" + now.fromNowSynced() + "</span>)</li>");


    elem.children().filter(":gt(50)").remove();
  }

  function log(text) {
    addItem(text, "");
  }

  function warn(text) {
    addItem(text, "warning-message");
  }

  function error(text) {
    addItem(text, "error-message");
  }

  this.warn = warn;
  this.error = error;
  this.log = log;
}

jq(document).ready(function () {
  debug = new Debug();

  jq(".main-button-box .debug-modal").on("click", function () {
    content_switch.switchContent("#debug-modal");
  });
  jq("#debug-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
