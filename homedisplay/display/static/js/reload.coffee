Reloader = ->
  onReceiveItemWS = (message) ->
    window.location.reload()

  startItem = ->
    ws_generic.register "reload", onReceiveItemWS

  stopItem = ->
    ws_generic.deRegister "reload"

  startItem()

  @stopItem = stopItem
  @startItem = startItem
  return @

jq =>
  @reloader_instance = new Reloader()
