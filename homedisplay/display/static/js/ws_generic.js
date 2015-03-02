var WsGeneric = function(options) {
  var ws4redis,
      callbacks = {},
      multiregister_callbacks = {},
      disconnected_since;

  function register(key, callback) {
    if (key in callbacks) {
      deRegister(key);
    }
    callbacks[key] = callback;
  }

  function multiRegister(key, unique_key, callback) {
    if (!(key in multiregister_callbacks)) {
      multiregister_callbacks[key] = {};
    }
    multiregister_callbacks[key][unique_key] = callback;
  }

  function deRegister(key) {
    delete callbacks[key];
  }

  function multiDeRegister(key, unique_key) {
    if (key in multiregister_callbacks) {
      delete multiregister_callbacks[key][unique_key];
    }
  }

  function onReceiveItemWS(message) {
    var data = JSON.parse(message);
    if (data.key in callbacks) {
      callbacks[data.key](data.content);
    }
    if (data.key in multiregister_callbacks) {
      for (unique_key in multiregister_callbacks[data.key]) {
        multiregister_callbacks[data.key][unique_key](data.content);
      }
    }
  }

  ws4redis = new WS4Redis({
    uri: websocket_root + "generic?subscribe-broadcast&publish-broadcast&echo",
    receive_message: onReceiveItemWS,
    heartbeat_msg: "--heartbeat--"
  });

  this.register = register;
  this.deRegister = deRegister;
  this.multiRegister = multiRegister;
  this.multiDeRegister = multiDeRegister;
};


jq(document).ready(function() {
  ws_generic = new WsGeneric();
});
