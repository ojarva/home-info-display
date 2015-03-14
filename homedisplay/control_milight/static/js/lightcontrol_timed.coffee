obj = this

obj.lightcontrol_timed_evening = null
obj.lightcontrol_timed_morning = null
obj.lightcontrol_timed_weekend_evening = null
obj.lightcontrol_timed_weekend_morning = null
obj.lightcontrol_timed_sort = null
obj.lightcontrol_timed = null

LightControlTimed = (options) ->
  # TODO: this should be refactored to use latest_data.start_datetime and .end_datetime instead of parsing from html.
  options = options || {}
  options.update_interval = options.update_interval || 1000
  options.backend_update_interval = options.backend_update_interval || SLOW_UPDATE
  main = jq options.elem
  update_interval = null
  backend_update_interval = null
  latest_data = null
  running = null

  if main.length == 0
    console.warn "!!! Invalid selector for LightControlTimed: " + options.elem
    debug.warn "Invalid selector for LightControlTimed: " + options.elem

  action = main.data("action")

  getNextStartDatetime = ->
    if latest_data? and latest_data.fields?
      return moment latest_data.fields.start_datetime

  getNextEndDatetime = ->
    if latest_data? and latest_data.fields?
      return moment latest_data.fields.end_datetime

  pauseOverride = ->
    main.find(".play-pause-control").slideDown()

  resumeOverride = (source) ->
    main.find(".play-pause-control").slideUp()
    if source == "ui"
      jq.post "/homecontroller/lightcontrol/timed/override-resume/#{action}"

  setStartTime = (start_time) ->
    start_time = start_time.split(":")
    main.find(".start-time-content").html(start_time[0] + ":" + start_time[1])

  setDuration = (duration) ->
    duration = parseInt duration
    hours = Math.floor(duration / 3600)
    duration -= hours * 3600
    minutes = ("00" + Math.round(duration / 60)).substr(-2)
    main.find(".duration-content").html "+#{hours}:#{minutes}"

  hideItem = ->
    jq(".timed-lightcontrols-main").find(options.elem).slideUp()

  showItem = ->
    jq(".timed-lightcontrols-main").find(options.elem).slideDown()

  getStartTime = ->
    return main.find(".start-time-content").html()

  getDuration = ->
    return main.find(".duration-content").html()

  getDurationSeconds = ->
    duration = getDuration().replace("+", "").split(":")
    duration = parseInt(duration[0]) * 3600 + parseInt(duration[1]) * 60
    return duration

  getStartTimeMoment = ->
    time = getStartTime().split(":")
    parsed_time = moment()
    parsed_time.hours(time[0])
    parsed_time.minutes(time[1])
    parsed_time.seconds(0)
    return parsed_time


  setRunning = (status) ->
    running = status
    if running
      main.find(".play-control i").removeClass("fa-toggle-off error-message").addClass("fa-toggle-on")
    else
      main.find(".play-control i").removeClass("fa-toggle-on").addClass("fa-toggle-off error-message")

  updateFields = (data) ->
    latest_data = data[0]
    setStartTime(data[0].fields.start_time)
    setDuration(data[0].fields.duration)
    setRunning(data[0].fields.running)
    if data[0].fields.is_overridden
      pauseOverride()
    else
      resumeOverride("backend")
    lightcontrol_timed_sort.sortTimers()

  update = ->
    jq.get "/homecontroller/lightcontrol/timed/get/#{action}", (data) ->
      updateFields data

  postUpdate = ->
    jq.post "/homecontroller/lightcontrol/timed/update/#{action}",
      start_time: getStartTime()
      duration: getDuration()
      running: running
    , (data) ->
      updateFields data

  adjustStartTime = (dir) ->
    # TODO: this is called too early, when data is not loaded yet.
    start_time = getStartTimeMoment()
    if dir == "plus"
      start_time.add 15, "minutes"
    else
      start_time.subtract 15, "minutes"
    setStartTime start_time.format("HH:mm")
    postUpdate()


  updateFromNow = ->
    if !latest_data
      main.find(".current-brightness").hide()
      return

    data = latest_data.fields
    start_time = getNextStartDatetime()
    end_time = getNextEndDatetime()
    now = clock.getMoment()
    show_progress_indicator = null
    content = main.find ".time-left"

    if now < end_time and end_time - now < getDurationSeconds() * 1000 # Currently running
      verb = "päättyy"
      if !running
        verb = "päättyisi"
        show_progress_indicator = false
      else
        show_progress_indicator = true

      content.html(verb + " " + end_time.fromNowSynced())
    else if now < start_time # Not yet started
      verb = "alkaa"
      show_progress_indicator = false
      if !running
        verb = "alkaisi"
      content.html "#{verb} " + start_time.fromNowSynced()
    else
      # Done for today.
      start_time.add(1, "days")
      verb = "alkaa"
      show_progress_indicator = false
      if !running
        verb = "alkaisi"

      content.html(verb + " " + start_time.fromNowSynced())

    if show_progress_indicator == true
      main.find(".play-control i").addClass("success-message")
      main.find(".current-brightness").show()

    else if show_progress_indicator == false
      main.find(".play-control i").removeClass("success-message")
      main.find(".current-brightness").hide()


  adjustDuration = (dir) ->
    time = getDuration().replace("+", "").split(":")
    parsed_time = moment()
    parsed_time.hours(time[0])
    parsed_time.minutes(time[1])
    if dir == "plus"
      if parsed_time.hours() < 2
        parsed_time.add 15, "minutes"

    else
      if (parsed_time.hours() == 0 and parsed_time.minutes() >= 15) or parsed_time.hours() > 0
        parsed_time.subtract 15, "minutes"

    formatted_time = parsed_time.format("H:mm")
    main.find(".duration-content").html "+#{formatted_time}"
    postUpdate()

  onReceiveItemUpdate = (data) ->
    updateFields data


  onReceiveOverride = (data) ->
    if data.action == "resume"
      resumeOverride "backend"
    else
      pauseOverride()

  startInterval = ->
    stopInterval()
    updateFromNow()
    update_interval = setInterval updateFromNow, options.update_interval
    update()
    backend_update_interval = setInterval update, options.backend_update_interval


  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval
    if backend_update_interval?
      backend_update_interval = clearInterval backend_update_interval

  main.find(".duration-time").find(".plus").on "click", ->
    content_switch.userActivity()
    adjustDuration "plus"

  main.find(".duration-time").find(".minus").on "click", ->
    content_switch.userActivity()
    adjustDuration "minus"


  main.find(".start-time").find(".plus").on "click", ->
    content_switch.userActivity()
    adjustStartTime "plus"

  main.find(".start-time").find(".minus").on "click", ->
    content_switch.userActivity()
    adjustStartTime "minus"


  main.find(".play-control").on "click", ->
    content_switch.userActivity()
    setRunning(!running)
    postUpdate()

  main.find(".play-pause-control").on "click", ->
    content_switch.userActivity()
    resumeOverride "ui"

  main.find(".open-light-dialog").on "click", ->
    content_switch.switchContent "#lightcontrol-modal"

  onReceiveBrightness = (data) ->
    # TODO: there is cases where this is not cleaned up properly
    main.find(".current-brightness").html "#{data}%"

  ws_generic.multiRegister "lightcontrol-timed-override", "lightcontrol-timed-override-#{action}", onReceiveOverride
  ws_generic.register "lightcontrol-timed-#{action}", onReceiveItemUpdate
  ws_generic.register "lightcontrol-timed-brightness-#{action}", onReceiveBrightness
  ge_refresh.register "lightcontrol-timed-#{action}", update

  startInterval()

  this.startInterval = startInterval
  this.stopInterval = stopInterval
  this.hideItem = hideItem
  this.showItem = showItem
  this.getNextStartDatetime = getNextStartDatetime
  this.getNextEndDatetime = getNextEndDatetime
  return this

ShowTimers = ->
  sortTimers = ->
    lightcontrol_timed.sort (a, b) ->
      return a.getNextStartDatetime() - b.getNextStartDatetime()

    # TODO: sort this out.
    lightcontrol_timed[2].hideItem()
    lightcontrol_timed[3].hideItem()
    lightcontrol_timed[0].showItem()
    lightcontrol_timed[1].showItem()

  this.sortTimers = sortTimers
  return this


jq =>
  @.lightcontrol_timed_sort = new ShowTimers()
  @.lightcontrol_timed_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning"})
  @.lightcontrol_timed_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening"})
  @.lightcontrol_timed_weekend_morning = new LightControlTimed({"elem": ".timed-lightcontrol-morning-weekend"})
  @.lightcontrol_timed_weekend_evening = new LightControlTimed({"elem": ".timed-lightcontrol-evening-weekend"})
  @.lightcontrol_timed = [@.lightcontrol_timed_evening, @.lightcontrol_timed_morning, @.lightcontrol_timed_weekend_evening, @.lightcontrol_timed_weekend_morning]
