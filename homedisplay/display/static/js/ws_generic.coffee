WsGeneric = (options) ->
  ws4redis = null
  callbacks = {}
  multiregister_callbacks = {}
  disconnected_since = null

  register = (key, callback) ->
    if callbacks[key]?
      deRegister key
    callbacks[key] = callback

  multiRegister = (key, unique_key, callback) ->
    if not multiregister_callbacks[key]?
      multiregister_callbacks[key] = {}

    multiregister_callbacks[key][unique_key] = callback


  deRegister = (key) ->
    delete callbacks[key]

  multiDeRegister = (key, unique_key) ->
    if multiregister_callbacks[key]?
      delete multiregister_callbacks[key][unique_key]

  onReceiveItemWS = (message) ->
    data = JSON.parse message
    if callbacks[data.key]?
      callbacks[data.key](data.content)

    if multiregister_callbacks[data.key]?
      for unique_key, func of multiregister_callbacks[data.key]
        func(data.content)

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
