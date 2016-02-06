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


  fetch = ->
    jq.get "/homecontroller/air_quality/get/sensor/co2/latest", (data) ->
      processCo2 data

    jq.get "/homecontroller/air_quality/get/sensor/temperature/latest", (data) ->
      processTemperature data

  fetchTrend = ->
    jq.get "/homecontroller/air_quality/get/sensor/co2/trend", (data) ->
      if data.status == "no_data"
        output.find(".trend").html ""
        return

      if data.delta < -0.025
        icon = "down"
      else if data.delta > 0.025
        icon = "up"
      else
        icon = "right"

      output.find(".trend").html "<i class='fa fa-arrow-#{icon}'></i>"

  update = ->
    fetch()
    fetchTrend()


  startInterval = ->
    update()
    update_timeout = setTimeout autoNoUpdates, 5000
    ws_generic.register "indoor_quality", fetchTrend # TODO: trend should be updated without polling
    ws_generic.register "indoor_co2", processCo2
    ws_generic.register "indoor_temperature", processTemperature
    ge_refresh.register "indoor_quality", update

  stopInterval = ->
    ws_generic.deRegister "indoor_quality"
    ws_generic.deRegister "indoor_co2"
    ws_generic.deRegister "indoor_temperature"
    ge_refresh.deRegister "indoor_quality"

  @fetch = fetch
  @fetchTrend = fetchTrend
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
