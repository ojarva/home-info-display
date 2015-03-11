ShutdownProgress = (options) ->
  options = options || {}
  options.timeout = options.timeout || 31000
  update_interval = null
  countdown_start = null

  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval
    jq("#shutdown-progress .progress-bar").css
      "width": "0%"

  stop = (source) ->
    if source != "backend"
      jq.post "/homecontroller/control_display/power/cancel-delayed", ->
        stopInterval()
        content_switch.switchContent "#main-content"
    else
      stopInterval()
      content_switch.switchContent "#main-content"

  shutdown = ->
    jq.post "/homecontroller/control_display/power/off"

  startup = ->
    jq.post "/homecontroller/control_display/power/on"

  restartDisplay = ->
    jq.post "/homecontroller/control_display/restart"

  update = ->
    time_left = options.timeout - (moment() - countdown_start)
    if time_left < -15 * 1000
      # Something went wrong with the backend
      stop "backend"

    if time_left < 0
      # WS message handles closing the dialog
      return

    percent = 100 * (options.timeout - time_left) / options.timeout
    jq("#shutdown-progress .progress-bar").css
      "width": percent + "%"


  startInterval = ->
    stopInterval()
    update()
    update_interval = setInterval ->
      update()
    , 100


  restart = (source) ->
    if source != "backend"
      jq.post "/homecontroller/control_display/power/delayed-shutdown", ->
        countdown_start = moment()
        startInterval()
    else
      countdown_start = moment()
      startInterval()

  onReceiveItemWS = (message) ->
    if message == "display-off" or message == "display-on" or message == "cancel-delayed"
      stop "backend"
    else if message == "delayed-shutdown"
      if not jq("#shutdown-progress").is(":visible")
        content_switch.switchContent "#shutdown-progress"
      restart "backend"

  ws_generic.register "shutdown", onReceiveItemWS

  @restart = restart
  @stop = stop
  @shutdown = shutdown
  @startup = startup
  @restartDisplay = restartDisplay
  return this

shutdown_progress = null

jq ->
  shutdown_progress = new ShutdownProgress()
  jq("#main-content .close").on "click", ->
    content_switch.switchContent "#shutdown-progress"
    shutdown_progress.restart()

  jq("#shutdown-progress .close, #shutdown-progress .cancel").on "click", ->
    shutdown_progress.stop()
    content_switch.switchContent "#main-content"

  jq("#shutdown-progress .yes").on "click", ->
    shutdown_progress.shutdown()

  jq(".display-power .shutdown-display").on "click", ->
    shutdown_progress.shutdown()

  jq(".display-power .startup-display").on "click", ->
    shutdown_progress.startup();

  jq(".display-power .restart-browser").on "click", ->
    shutdown_progress.restartDisplay()
