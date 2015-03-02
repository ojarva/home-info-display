var Reloader = function() {
  "use strict";
  function onReceiveItemWS(message) {
    window.location.reload();
  }

  function startItem() {
    ws_generic.register("reload", onReceiveItemWS);
  }

  function stopItem() {
    ws_generic.deRegister("reload");
  }

  startItem();

  this.stopItem = stopItem;
  this.startItem = startItem;
};

var reloader_instance;
jq(document).ready(function() {
  "use strict";
  reloader_instance = new Reloader();
});
