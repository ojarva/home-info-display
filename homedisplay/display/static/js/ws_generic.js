var WsGeneric = function(options) {
  var ws4redis,
      callbacks = {};

  function register(key, callback) {
    if (key in callbacks) {
      deRegister(key);
    }
    callbacks[key] = callback;
  }

  function deRegister(key) {
    delete callbacks[key];
  }

  function onReceiveItemWS(message) {
    var data = JSON.parse(message);
    if (data.key in callbacks) {
      callbacks[data.key](data.content);
    }
  }

  ws4redis = new WS4Redis({
    uri: websocket_root + "generic?subscribe-broadcast&publish-broadcast&echo",
    receive_message: onReceiveItemWS,
    heartbeat_msg: "--heartbeat--"
  });
  this.register = register;
  this.deRegister = deRegister;
};

var ws_generic;

$(document).ready(function() {
  ws_generic = new WsGeneric();
});
