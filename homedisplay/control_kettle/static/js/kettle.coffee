Kettle = (elem) ->

  onReceiveItemWS = (message) ->
    processData message

  processData = (data) ->
    if data.status == "ready" and data.present and data.water_level != "empty" and data.water_level != "too_low"
      jq(elem).find(".action-on").removeClass("disabled")
      jq(elem).find(".disabled-mode").hide()
    else
      jq(elem).find(".action-on").addClass("disabled")
      jq(elem).find(".disabled-mode").show()

    if data.present
      jq(elem).find(".online-status").show()
      jq(elem).find(".offline-status").hide()
      if data.water_level == "empty" or data.water_level == "too_low"
        water_level = "0"
      else if data.water_level == "half"
        water_level = "2"
      else
        water_level = "4"
      jq(elem).find(".waterlevel-content").removeClass().addClass("waterlevel-content fa fa-battery-#{water_level}")
      jq(elem).find(".temperature-content").html(data.temperature)
    else
      jq(elem).find(".online-status").hide()
      jq(elem).find(".offline-status").show()


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

  jq(elem).find(".action-on").each ->
    jq(@).click ->
      temperature = jq(@).data "temperature"
      jq.post "/homecontroller/kettle/control/on/#{temperature}"

  jq(elem).find(".action-off").each ->
    jq(@).click ->
      jq.post "/homecontroller/kettle/control/off"


  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

jq =>
  @kettle_i = new Kettle "#kettle"
  @kettle_i.startInterval()
