IndoorAirQuality = (options) ->
  options = options or {}
  options.main_elem = options.main_elem or ".indoor-quality"
  options.update_timeout = options.update_timeout or 2 * 60 * 1000
  options.co2_green = options.co2_green or 1000
  options.co2_error = options.co2_error or 1500

  output = jq options.main_elem
  update_interval = null
  update_timeout = null

  clearAutoNoUpdates = ->
    if update_timeout?
      update_timeout = clearTimeout update_timeout

  autoNoUpdates = ->
    output.find(".status").html "<i class='fa fa-times warning-message'></i> "

  processCo2 = (data) ->
    if not data?
      console.warn "!!! No indoor air quality information available."
      autoNoUpdates()
      return

    co2 = data.value

    if co2 < options.co2_green
      co2_out = "<i class='fa fa-check success-message'></i>"
      output.removeClass "warning-message error-message"
    else if co2 < options.co2_error
      co2_out = "<i class='fa fa-exclamation-triangle'></i>"
      output.removeClass("error-message").addClass "warning-message"
    else
      co2_out = "<i class='fa fa-ban'></i>"
      output.removeClass("warning-message").addClass "error-message"

    output.find(".status").html co2_out
    output.find(".co2").data "value", co2
    .html Math.round(co2) + "ppm"

    clearAutoNoUpdates()
    update_timeout = setTimeout autoNoUpdates, options.update_timeout # 2,5 minutes


  processTemperature = (data) ->
    if not data?
      console.warn "!!! No indoor air quality information available."
      autoNoUpdates()
      return

    temperature = data.value
    output.find(".temperature")
    .data "value", temperature
    .html Math.round(parseFloat(temperature) * 10) / 10 + "&degC"

  processHumidity = (data) ->
    if not data?
      console.warn "!!! No humidity information available"
      return
    humidity = data.value
    output.find(".humidity")
    .data "value", humidity
    .html Math.round(parseFloat(humidity) * 10) / 10 + "%"


  fetch = ->
    jq.get "/homecontroller/air_quality/get/sensor/co2/latest", (data) ->
      processCo2 data

    jq.get "/homecontroller/air_quality/get/sensor/temperature/latest", (data) ->
      processTemperature data

    jq.get "/homecontroller/air_quality/get/sensor/humidity/latest", (data) ->
      processHumidity data


  update = ->
    fetch()

  startInterval = ->
    update()
    update_timeout = setTimeout autoNoUpdates, 30000
    ws_generic.register "indoor_co2", processCo2
    ws_generic.register "indoor_temperature", processTemperature
    ws_generic.register "indoor_humidity", processHumidity
    ge_refresh.register "indoor_quality", update

  stopInterval = ->
    ws_generic.deRegister "indoor_quality"
    ws_generic.deRegister "indoor_co2"
    ws_generic.deRegister "indoor_temperature"
    ws_generic.deRegister "indoor_humidity"
    ge_refresh.deRegister "indoor_quality"

  @fetch = fetch
  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

closeIndoorAirQualityModal = ->
  jq("#indoor-quality-modal .close").trigger("click")

jq =>
  @indoor_air_quality = new IndoorAirQuality()
  @indoor_air_quality.startInterval()

  jq(".indoor-quality").on "click", ->
    jq.get "/homecontroller/air_quality/get/dialog/contents", (data) ->
      jq("#indoor-quality-modal .air-quality-graph-content").html data
      content_switch.switchContent "#indoor-quality-modal"

  jq("#indoor-quality-modal .close").on "click", ->
    jq("#indoor-quality-modal .air-quality-graph-content").children().remove()
    content_switch.switchContent "#main-content"
