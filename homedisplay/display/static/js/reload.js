var Reloader = function() {
  var ws4redis;
  function onReceiveItemWS(message) {
    window.location.reload();
  }

  ws4redis = new WS4Redis({
    uri: websocket_root+'reload?subscribe-broadcast&publish-broadcast&echo',
    receive_message: onReceiveItemWS,
    heartbeat_msg: "--heartbeat--"
  });

  function stop() {
    try {
      ws4redis.close();
    } catch (e) {
    }
  }

  this.stop = stop;
};

var reloader_instance;
$(document).ready(function() {
  reloader_instance = new Reloader();
});
