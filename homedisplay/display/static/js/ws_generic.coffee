WsGeneric = (options) ->
  ws4redis = null
  callbacks = {}
  multiregister_callbacks = {}
  disconnected_since = null

  register = (key, callback) ->
    if key in callbacks
      deRegister key
    callbacks[key] = callback

  multiRegister = (key, unique_key, callback) ->
    if !(key in multiregister_callbacks)
      multiregister_callbacks[key] = {}

    multiregister_callbacks[key][unique_key] = callback


  deRegister = (key) ->
    delete callbacks[key]

  multiDeRegister = (key, unique_key) ->
    if key in multiregister_callbacks
      delete multiregister_callbacks[key][unique_key]

  onReceiveItemWS = (message) ->
    data = JSON.parse message
    if data.key in callbacks
      callbacks[data.key](data.content)

    if data.key in multiregister_callbacks
      for unique_key in multiregister_callbacks[data.key]
        multiregister_callbacks[data.key][unique_key](data.content)

  ws4redis = new WS4Redis
      uri: websocket_root + "generic?subscribe-broadcast&publish-broadcast&echo"
      receive_message: onReceiveItemWS
      heartbeat_msg: "--heartbeat--"

  this.register = register
  this.deRegister = deRegister
  this.multiRegister = multiRegister
  this.multiDeRegister = multiDeRegister
  return this

obj = this

jq ->
  obj.ws_generic = new WsGeneric()
