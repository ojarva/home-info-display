ShowRealtimePing = (options) ->

  options = options || {}
  options.invalid_timeout = options.invalid_timeout || 10000
  container = jq options.output
  invalid_timeout = null

  noUpdates = (warning_class) ->
    warning_class = warning_class || "error"
    container.html "<i class='fa fa-times-circle " + warning_class + "-message'></i>"

  autoNoUpdates = ->
    noUpdates "warning"

  update = (message) ->
    if message == "no_pings"
      noUpdates()
      return

    if invalid_timeout?
      invalid_timeout = clearTimeout invalid_timeout

    ping = Math.round(parseFloat(message) * 10) / 10
    container.html "<i class='fa fa-check-circle success-message'></i> #{ping}ms"
    invalid_timeout = setTimeout autoNoUpdates, options.invalid_timeout


  startInterval = ->
    ws_generic.register "ping", update


  stopInterval = ->
    ws_generic.deRegister "ping"


  @startInterval = startInterval
  @stopInterval = stopInterval
  return this

RefreshInternet = (options) ->
  options = options || {}
  options.invalid_timeout = options.invalid_timeout || 2 * 60 * 1000
  update_timeout = null
  output = jq(".internet-connection")

  setSignal = (level) ->
    output.find(".signal-bars div").removeClass("active").addClass("inactive")
    for a in [1..level]
      output.find(".signal-bars .signal-" + a).addClass("active").removeClass("inactive")

  clearAutoNoUpdates = ->
    if update_timeout?
      update_timeout = clearTimeout update_timeout



  autoNoUpdates = ->
    clearAutoNoUpdates()
    output.find(".signal-bars").slideUp()
    output.find(".signal-bars").data "is-hidden", true
    output.find(".connected").html "<i class='fa fa-times warning-message'></i> Ei tietoja"


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
  return this

refresh_internet = null
show_pings = null
jq ->
  refresh_internet = new RefreshInternet
    output: ".internet-connection"
  refresh_internet.startInterval()

  show_pings = new ShowRealtimePing
    output: ".internet-connection .ping"
  show_pings.startInterval()

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
