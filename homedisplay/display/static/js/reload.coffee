Reloader = ->
  onReceiveItemWS = (message) ->
    window.location.reload()

  startItem = ->
    ws_generic.register "reload", onReceiveItemWS

  stopItem = ->
    ws_generic.deRegister "reload"

  startItem()

  this.stopItem = stopItem
  this.startItem = startItem
  return this

jq =>
  this.reloader_instance = new Reloader()
