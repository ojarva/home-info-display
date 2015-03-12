# TODO: implement multiRegister/multiDeRegister
GenericRefresh = (options) ->
  callbacks = {}

  setRefreshCallback = (callback) ->
    refresh_callback = callback

  register = (key, callback) ->
    if callbacks[key]?
      deRegister(key)

    callbacks[key] = callback


  deRegister = (key) ->
    delete callbacks[key]


  requestUpdate = ->
    for k of callbacks
      callbacks[k]()

    if refresh_callback?
      refresh_callback()

  ws_generic.register "generic_refresh", requestUpdate

  this.deRegister = deRegister
  this.register = register
  this.requestUpdate = requestUpdate
  this.setRefreshCallback = setRefreshCallback
  return this

jq =>
  this.ge_refresh = new GenericRefresh()
