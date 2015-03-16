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

  @deRegister = deRegister
  @register = register
  @requestUpdate = requestUpdate
  @setRefreshCallback = setRefreshCallback
  return @

jq =>
  @ge_refresh = new GenericRefresh()
