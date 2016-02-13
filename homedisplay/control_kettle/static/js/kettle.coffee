Kettle = (elem) ->

  onReceiveItemWS = (message) ->
    processData message

  processData = (data) ->
    if data.status == "ready" and data.present and data.water_level > 0.1
      jq(elem).find(".action-on").removeClass("disabled")
      jq(elem).find(".disabled-mode").hide()
    else
      jq(elem).find(".action-on").addClass("disabled")
      jq(elem).find(".disabled-mode").show()

    if data.present
      jq(elem).find(".online-status").show()
      jq(elem).find(".offline-status").hide()
      if not data.water_level?
        water_level = "?"
      else if data.water_level < 0.1
        water_level = "0dl"
      else
        water_level = 18 * data.water_level + "dl"
      jq(elem).find(".waterlevel-content").html(water_level)
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
