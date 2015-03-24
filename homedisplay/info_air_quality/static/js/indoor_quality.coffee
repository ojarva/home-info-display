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

  drawGraph = (data, goptions) ->
    goptions = goptions or {}
    goptions.xlabel = goptions.xlabel or "Aika"
    goptions.ylabel = goptions.ylabel or "Arvo"

    elem = jq goptions.selector

    if not data?
      debug.warn "No data available for indoor air quality graphs"
      console.warn "!!! No data available for indoor air quality graphs!"
      elem.children().remove()
      elem.slideUp()
      elem.parent().find(".data-error").slideDown()
      return

    elem.slideDown()
    elem.parent().find(".data-error").slideUp()

    x = []
    y = []
    nv.addGraph ->
      chart = nv.models.lineChart()
      .useInteractiveGuideline true
      .showLegend false
      .interpolate "bundle"
      .transitionDuration 350
      .showYAxis true
      .showXAxis true
      .x (d, i) ->
        return (new Date(d[0]).getTime())
      .y (d, i) ->
        return d[1]

      chart.xAxis
      .axisLabel goptions.xlabel
      .tickFormat (d) ->
        return d3.time.format("%H:%M")(new Date(d))

      chart.yAxis
      .axisLabel goptions.ylabel
      .tickFormat d3.format(".02f")

      processed_data = []
      jq.each data, ->
        processed_data.push [@timestamp, @value]

      processed_data.reverse()
      myData = [
        "key": goptions.key
        "bar": true
        "color": "#ccf"
        "values": processed_data
      ]

      d3.select goptions.selector
      .datum myData
      .call chart

      nv.utils.windowResize chart.update
      return chart

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
    jq.get "/homecontroller/indoor_quality/get/sensor/co2/latest", (data) ->
      processCo2 data

    jq.get "/homecontroller/indoor_quality/get/sensor/temperature/latest", (data) ->
      processTemperature data

  fetchTrend = ->
    jq.get "/homecontroller/indoor_quality/get/sensor/co2/trend", (data) ->
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

  refreshData = (key) ->
    data_output = jq ".indoor-air-#{key}"
    data_output.find("svg").hide()
    data_output.find(".spinner").show()
    jq.get "/homecontroller/indoor_quality/get/sensor/#{key}", (data) ->
      if data.length > 12
        data_output.find(".latest").html Math.round(data[data.length-1].value * 10) / 10
        data_output.find(".data-error").hide()
        data_output.find(".spinner").hide()
        data_output.find("svg").show()
        drawGraph data,
         key: key
         selector: ".indoor-air-#{key} svg"
      else
        data_output.find(".latest").html "-"
        data_output.find("svg").slideUp()
        data_output.find(".spinner").slideUp()
        data_output.find(".data-error").slideDown()

  refreshAllData = ->
    jq.get "/homecontroller/indoor_quality/get/sensor/keys", (data) ->
      jq.each data, ->
        refreshData @

  @fetch = fetch
  @fetchTrend = fetchTrend
  @refreshData = refreshData
  @refreshAllData = refreshAllData
  @drawGraph = drawGraph
  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

closeIndoorAirQualityModal = ->
  jq("#indoor-quality-modal .close").trigger("click")

jq =>
  @indoor_air_quality = new IndoorAirQuality()
  @indoor_air_quality.startInterval()

  jq(".indoor-quality").on "click", ->
    jq.get "/homecontroller/indoor_quality/get/dialog/contents", (data) ->
      jq("#indoor-quality-modal .air-quality-graph-content").html data
      indoor_air_quality.refreshAllData()
      content_switch.switchContent "#indoor-quality-modal"

  jq("#indoor-quality-modal .close").on "click", ->
    jq("#indoor-quality-modal .air-quality-graph-content").children().remove()
    content_switch.switchContent "#main-content"
