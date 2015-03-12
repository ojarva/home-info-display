ServerPower = (options) ->
  options = options || {}
  options.update_interval = options.update_interval || FAST_UPDATE
  main_elem = jq options.main_elem
  interval = null
  spinner_until_status_from = null
  button_in_progress_timeout = null


  removeSpinners = ->
    spinner_until_status_from = null
    main_elem.find(".action-button i").each ->
      jq(this).removeClass().addClass(jq(this).data("original-classes"))

    if button_in_progress_timeout?
      button_in_progress_timeout = clearTimeout button_in_progress_timeout


  setSpinners = ->
    main_elem.find(".action-button i").removeClass().addClass("fa fa-spinner fa-spin")
    # If status does not change, remove spinner.
    button_in_progress_timeout = setTimeout removeSpinners, 60 * 1000


  showButton = (button_name) ->
    main_elem.find(".action-button").not(".#{button_name}").hide()
    main_elem.find(".#{button_name}").show()


  setStatus = (data) ->
    if data.in_progress
      if spinner_until_status_from
        # Waiting for status change
        if data.in_progress != spinner_until_status_from
          # Status changed
          removeSpinners()

       else
        # Should wait for status change
        spinner_until_status_from = data.in_progress
        setSpinners()

    if data.status == "down"
      showButton "startup"
     else if data.status == "not_responding"
      showButton "unknown"
     else if data.status == "running"
      showButton "shutdown"


  refreshServerPower = ->
    jq.get "/homecontroller/server_power/status", (data) ->
      setStatus data


  onReceiveItemWS = (message) ->
    setStatus message


  stopInterval = ->
    if interval?
      interval = clearInterval interval

    ws_generic.deRegister "server_power"


  startInterval = ->
    stopInterval()
    refreshServerPower()
    interval = setInterval refreshServerPower, options.update_interval
    ws_generic.register "server_power", onReceiveItemWS


  main_elem.find(".action-button i").each ->
    jq(this).data
      "original-classes": jq(this).attr("class")

  main_elem.find(".startup").on "click", ->
    spinner_until_status_from = "down"
    setSpinners()
    jq.post "/homecontroller/server_power/startup"

  main_elem.find(".shutdown").on "click", ->
    spinner_until_status_from = "running"
    setSpinners()
    jq.post "/homecontroller/server_power/shutdown"


  @startInterval = startInterval
  @stopInterval = stopInterval
  return this

jq =>
  this.server_power = new ServerPower
    main_elem: ".server-power"
  this.server_power.startInterval()
