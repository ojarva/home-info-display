ShowRealtimeStats = (options) ->

  options = options or {}
  options.invalid_ping_timeout = options.invalid_ping_timeout or 10000
  options.invalid_speed_timeout = options.invalid_speed_timeout or 30000
  ping_container = jq options.ping_output
  speed_container = jq options.speed_output
  invalid_ping_timeout = null
  invalid_speed_timeout = null
  filesize_options =
    bits: true
    round: 0
    output: "object"

  noPingUpdates = (warning_class) ->
    warning_class = warning_class or "error"
    ping_container.html "<i class='fa fa-times-circle #{warning_class}-message'></i>"

  autoNoPingUpdates = ->
    noPingUpdates "warning"

  noSpeedUpdates = (warning_class) ->
    warning_class = warning_class or "error"
    speed_container.find(".value").html "<i class='fa fa-times-circle #{warning_class}-message'></i>"

  autoNoSpeedUpdates = ->
    noSpeedUpdates "warning"

  update = (message) ->
    if message == "no_pings"
      noPingUpdates()
      return

    if invalid_ping_timeout?
      invalid_ping_timeout = clearTimeout invalid_ping_timeout

    ping = Math.round(parseFloat(message))
    ping_container.html "<i class='fa fa-check-circle success-message'></i> #{ping}ms"
    invalid_ping_timeout = setTimeout autoNoPingUpdates, options.invalid_ping_timeout

  updateSpeed = (data) ->
    if data.internet?
      if invalid_speed_timeout?
        invalid_speed_timeout = clearTimeout invalid_speed_timeout
      speed_in = data.internet.speed_in / 8
      speed_out = data.internet.speed_out / 8

      speed_in = filesize speed_in, filesize_options
      speed_out = filesize speed_out, filesize_options

      speed_container.find(".upload .value").html speed_out.value
      speed_container.find(".upload .unit").html "#{speed_out.suffix}/s"
      speed_container.find(".download .value").html speed_in.value
      speed_container.find(".download .unit").html "#{speed_in.suffix}/s"

      invalid_speed_timeout = setTimeout autoNoSpeedUpdates, options.invalid_speed_timeout

  startInterval = ->
    ws_generic.register "ping", update
    ws_generic.register "internet-speed", updateSpeed

  stopInterval = ->
    ws_generic.deRegister "ping"
    ws_generic.deRegister "internet-speed"


  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

RefreshInternet = (options) ->
  options = options or {}
  options.invalid_timeout = options.invalid_timeout or 2 * 60 * 1000
  update_timeout = null
  output = jq ".internet-connection"

  setSignal = (level) ->
    output.find ".signal-bars div"
    .removeClass "active"
    .addClass "inactive"
    for a in [1..level]
      output.find ".signal-bars .signal-#{a}"
      .addClass "active"
      .removeClass "inactive"

  clearAutoNoUpdates = ->
    if update_timeout?
      update_timeout = clearTimeout update_timeout



  autoNoUpdates = ->
    clearAutoNoUpdates()
    output.find(".signal-bars").slideUp()
    output.find(".signal-bars").data "is-hidden", true
    output.find(".connected").html "<i class='fa fa-times warning-message'></i> "


  processData = (data) ->
    if not data? or (data.status? and data.status == "error")
      debug.warn "No internet connection information is available"
      console.warn "!!! No internet connection information available"
      autoNoUpdates()
      return

    signal_bars = output.find ".signal-bars"
    if signal_bars.data "is-hidden"
      signal_bars.slideDown()
      signal_bars.data "is-hidden", false

    cs = data.fields.connect_status

    if cs == "connected"
      cs_out = "<i class='fa fa-check-circle success-message'></i>"
     else if cs == "connecting"
      cs_out = "<i class='fa fa-spin fa-cog warning-message'></i>"
     else
      cs_out = "<i class='fa fa-times error-message'></i>"

    output.find(".connected").html cs_out
    output.find(".mode").html data.fields.mode
    setSignal data.fields.signal
    clearAutoNoUpdates()
    update_timeout = setTimeout autoNoUpdates, options.invalid_timeout



  update = ->
    jq.get "/homecontroller/internet_connection/status", (data) ->
      processData data

  startInterval = ->
    stopInterval()
    update()
    ws_generic.register "internet", processData
    ge_refresh.register "internet", update


  stopInterval = ->
    ws_generic.deRegister "internet"
    ge_refresh.deRegister "internet"


  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

jq =>
  @refresh_internet = new RefreshInternet
    output: ".internet-connection"
  @refresh_internet.startInterval()

  @show_internet_info = new ShowRealtimeStats
    ping_output: ".internet-connection .ping"
    speed_output: ".internet-connection .speed"
  @show_internet_info.startInterval()

  jq(".internet-connection").on "click", ->
    charts = [["idler", "Internet/idler_last_10800.png"],
                  ["Google", "Internet/google_last_10800.png"],
                  ["Saunalahti", "Internet/saunalahti_last_10800.png"],
                  ["Funet", "Internet/funet_last_10800.png"],
                  ["idler", "Internet/idler_last_108000.png"],
                  ["Google", "Internet/google_last_108000.png"],
                  ["Saunalahti", "Internet/saunalahti_last_108000.png"],
                  ["Funet", "Internet/funet_last_108000.png"]
                  ]
    content = ""
    timestamp = new Date() - 0
    jq.each charts, ->
      description = @[0]
      link = @[1]
      content += "<div class='smokeping-chart'><h4>#{description}</h4><img src='/smokeping/images/#{link}?#{timestamp}'></div>"

    jq("#internet-connection-modal .smokeping-charts").html content
    content_switch.switchContent "#internet-connection-modal"

  jq("#internet-connection-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
