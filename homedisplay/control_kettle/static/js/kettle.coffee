Kettle = (elem) ->

  onReceiveItemWS = (message) ->
    processData message



  processData = (data) ->
    jq(elem).find("#temperature-content").html(data.temperature)
    jq(elem).find("#waterlevel-content").html(data.waterlevel)

  update = ->
    jq.get "/homecontroller/kettle/status", (data) ->
      processData data

  startInterval = ->
    update()
    ws_generic.register "kettle-info", onReceiveItemWS
    ge_refresh.register "kettle-info", update

  stopInterval = ->
    ws_generic.deRegister "kettle-info"
    ge_refresh.deRegister "kettle-info"

  jq(elem).find(".action-button").each ->
    jq(@).click ->
      console.log "Clicked ", @
      temperature = jq(@).data "temperature"
      if temperature?
        console.log "enabling ", temperature

  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

jq =>
  @kettle_i = new Kettle "#kettle"
  @kettle_i.startInterval()
