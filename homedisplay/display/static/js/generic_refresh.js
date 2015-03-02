// TODO: implement multiRegister/multiDeRegister
var GenericRefresh = function(options) {
  var callbacks = {},
      refresh_callback;

  function setRefreshCallback(callback) {
    refresh_callback = callback;
  }

  function register(key, callback) {
    if (key in callbacks) {
      deRegister(key);
    }
    callbacks[key] = callback;
  }

  function deRegister(key) {
    delete callbacks[key];
  }

  function requestUpdate() {
    for (k in callbacks) {
      callbacks[k]();
    }
    if (refresh_callback) {
      refresh_callback();
    }
  }

  ws_generic.register("generic_refresh", requestUpdate);

  this.deRegister = deRegister;
  this.register = register;
  this.requestUpdate = requestUpdate;
  this.setRefreshCallback = setRefreshCallback;
};

var ge_refresh;

jq(document).ready(function() {
  ge_refresh = new GenericRefresh();
});
