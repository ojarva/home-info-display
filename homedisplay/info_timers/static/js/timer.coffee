obj = @
obj.timers = null

Timer = (parent_elem, options) ->
  created_by_backend = false
  start_time = null
  update_interval = null
  backend_interval = null
  alarm_interval = null
  running = false
  id_uniq = uuid()
  id = null
  timer_elem = null
  options = options or {}
  options.delay = options.delay or 1000
  options.backend_interval = options.backend_interval or FAST_UPDATE


  clearItemIntervals = ->
    if update_interval?
      update_interval = clearInterval update_interval
    if alarm_interval?
      alarm_interval = clearInterval alarm_interval

  deleteItem = (item_source) ->
    timer_elem.slideUp "fast", ->
      jq(@).remove()
    clearItemIntervals()
    if backend_interval?
      backend_interval = clearInterval backend_interval

    if item_source != "backend" and id?
      jq.delete "/homecontroller/timer/delete/#{id}"

    ws_generic.deRegister "timer-#{id}"
    ge_refresh.deRegister "timer-#{id}"


  zeroPad = (num, places) ->
    zero = places - num.toString().length + 1
    return Array(+(zero > 0 and zero)).join("0") + num

  updateTimerContent = (diff, prefix) ->
    if options.auto_remove? and prefix == "-"
      if diff > options.auto_remove
        deleteItem() # Delete item automatically if auto remove overrun is exceeded.

    time_diff = start_time - clock.getDate()
    if time_diff > 1000
      # not yet started
      timer_elem.hide()
    else
      timer_elem.slideDown()

    hours = Math.floor diff / 3600
    diff = diff - hours * 3600
    minutes = Math.floor diff / 60
    diff = diff - minutes * 60
    seconds = Math.floor diff
    timer = prefix + zeroPad(hours, 2) + ":" + zeroPad(minutes, 2) + ":" + zeroPad(seconds, 2)
    if timer_type == "timer"
      timer_elem.find(".timer-timeleft").html timer
    else
      if hours < 0
        timer_elem.find(".stopclock-content").html "00:00:00"
      else
        timer_elem.find(".stopclock-content").html timer

  update = ->
    if !running
      return
    now = clock.getDate()
    prefix = ""

    if timer_type == "timer"
      diff = parseInt(options.duration) - (now - start_time) / 1000
      percent = Math.round (parseFloat(diff) / parseFloat(options.duration)) * 100
      if percent > 100
        percent = 100
      if diff < 0
        prefix = "-"
        diff *= -1
      if percent > 0
        timer_elem.find ".progress-bar"
        .css "width", "#{percent}%"
        .removeClass "progress-bar-danger"
        .addClass "progress-bar-success"
        timer_elem.removeClass "timer-overtime"
      else
        timer_elem.find ".progress-bar"
        .removeClass "progress-bar-success"
        .addClass "progress-bar-danger"
        .css "width", "100%"
        timer_elem.addClass "timer-overtime"
        # TODO: play alarm

    else if timer_type == "stopclock"
      diff = (now - start_time) / 1000

    updateTimerContent diff, prefix



  startItem = (source) ->
    clearItemIntervals()
    running = true
    update() # Immediately run first update
    update_interval = setInterval update, options.delay
    backend_interval = setInterval refreshFromBackend, options.backend_interval
    timer_elem.data "start-timestamp", start_time
    if timer_type == "timer"
      timer_elem.data "end-timestamp", (start_time.getTime() / 1000) + options.duration

    timer_elem.find ".stopclock-stop i"
    .addClass "fa-stop"
    .removeClass "fa-trash"

    timers.sortTimers()
    if source != "backend" and id?
      # If action was triggered by user, update backend
      jq.patch "/homecontroller/timer/start/#{id}"


  stopItem = (source) ->
    #TODO: support for timers
    if source != "backend" and timer_elem.find(".stopclock-stop i").hasClass("fa-trash")
      # Delete stopwatch only if event was initiated by user *and* stopwatch was already stopped.
      deleteItem "ui"
      return

    timer_elem.stop(true)
    .css "background-color", timer_elem.data("original-bg-color")
    .effect "highlight",
      color: "#cc0000"
    , 500
    running = false
    clearItemIntervals()
    # If item is stopwatch, change icon
    timer_elem.find ".stopclock-stop i"
    .removeClass "fa-stop"
    .addClass "fa-trash"

    if source != "backend"
      # Initiated by user - update backend
      jq.patch "/homecontroller/timer/stop/#{id}", (data) ->
        diff = ((new Date(data[0].fields.stopped_at)) - (new Date(data[0].fields.start_time))) / 1000
        updateTimerContent diff, ""

    else if options.stopped_at
      diff = (new Date(options.stopped_at) - start_time) / 1000
      updateTimerContent diff, ""

  refreshFromBackend = ->
    if id? # Don't refresh if no data is available.
      jq.ajax
        url: "/homecontroller/timer/get/#{id}"
        success: (data) ->
          start_time = new Date data[0].fields.start_time
          if data[0].fields.running
            if !running
              startItem "backend"
          else
            if running
              stopItem "backend"
        statusCode:
          404: ->
            deleteItem "backend"

  onReceiveItemWS = (message) ->
    source = "backend"

    if message == "delete"
      deleteItem source
      return

    data = message[0]
    start_time = new Date data.fields.start_time
    if data.fields.running
      # Timer should be running.
      startItem source
      return

    # Timer is stopped
    timer_elem.stop(true).css "background-color", timer_elem.data("original-bg-color")
    .effect "highlight",
      color: "#cc0000"
    , 500

    running = false
    clearItemIntervals()
    timer_elem.find ".stopclock-stop i"
    .removeClass "fa-stop"
    .addClass "fa-trash"
    if data.fields.stopped_at
      diff = (new Date(data.fields.stopped_at) - start_time) / 1000
      updateTimerContent diff, ""

  setId = (new_id) ->
    # Set backend id to local object.
    id = new_id
    timers.addTimerId id
    ws_generic.register "timer-#{id}", onReceiveItemWS
    ge_refresh.register "timer-#{id}", refreshFromBackend

  getId = ->
    return id

  restartItem = ->
    timer_elem.stop(true).css("background-color", timer_elem.data("original-bg-color"))
    .effect "highlight",
      color: "#00cc00"
    , 500
    startItem "backend" # Prevent duplicate updates to backend
    if id?
      jq.patch "/homecontroller/timer/restart/#{id}", (data) ->
        start_time = new Date(data[0].fields.start_time)
    else
      start_time = clock.getDate()
    return

  create = ->
    # Creates HTML elements and starts timer.
    if timer_type == "timer"
      jq(parent_elem).append """<div class='row timer-item' style='display:none' id='timer-#{id_uniq}'>
  <div class='col-md-8'>
    <div class='timer-info'> #{options.name} <span style='float: right' class='timer-timeleft'>---</span>
    </div>
    <div class='progress hidden-xs hidden-sm'>
      <div class='progress-bar' role='progressbar' aria-valuenow='100' aria-valuemin='0' aria-valuemax='100' style='width:100%'>
      </div>
    </div>
  </div>
  <div class='col-md-2 timer-stop timer-control animate-click'>
    <i class='fa fa-trash'></i>
  </div>
  <div class='col-md-2 timer-restart timer-control animate-click'>
    <i class='fa fa-refresh'></i>
  </div>
</div>"""
      timer_elem = jq "#timer-#{id_uniq}"
      timer_elem.find(".timer-stop").click ->
        deleteItem "ui"

      if options.no_refresh
        timer_elem.find(".timer-restart").hide()
      else
        timer_elem.find(".timer-restart").click ->
          restartItem()

    else
      jq(parent_elem).append """<div class='row timer-item' style='display:none' id='timer-#{id_uniq}'>
  <div class='col-md-8 stopclock timer-main center-content stopclock-content'>
    00:00:00
  </div>
  <div class='col-md-2 timer-control animate-click stopclock-stop'>
    <i class='fa fa-stop'></i>
  </div>
  <div class='col-md-2 timer-control animate-click stopclock-restart'>
    <i class='fa fa-refresh'></i>
  </div>
</div>"""

      timer_elem = jq "#timer-#{id_uniq}"
      timer_elem.find(".stopclock-stop").click ->
        stopItem "ui"

      timer_elem.find(".stopclock-restart").click ->
        restartItem()

    timer_elem.data "original-bg-color", timer_elem.css("background-color")

    timer_elem.stop(true).slideDown("fast")

    if created_by_backend
      timer_elem.addClass "timer-backend-id-#{id}"
      if options.running
        startItem "backend"
      else
        stopItem "backend"

    else
      restartItem()
      jq.post "/homecontroller/timer/create",
        name: options.name
        duration: options.duration
      , (data) ->
        setId data[0].pk
        timer_elem.addClass "timer-backend-id-#{data[0].pk}"
        start_time = new Date data[0].fields.start_time


  if options.id
    setId options.id
    created_by_backend = true


  if options.start_time
    start_time = options.start_time

  if options.duration
    timer_type = "timer"
  else
    timer_type = "stopclock"

  create()

  @deleteItem = deleteItem
  @restartItem = restartItem
  @startItem = startItem
  @getId = getId
  return @

Timers = (options) ->
  options = options or {}
  options.update_interval = options.update_interval or 3 * 60 * 1000
  timer_holder = options.timer_holder or "#timer-holder"
  stopclock_holder = options.stopclock_holder or "#stopclock-holder"
  created_timer_items = []

  hasTimer = (id) ->
    currently_running = jq ".timer-backend-id-#{id}"
    if id of created_timer_items
      return true

    if currently_running.length == 0
      return false
    else
      return true

  refreshFromServer = ->
    jq.getJSON "/homecontroller/timer/list", (data) ->
      jq.each data, ->
        id = @pk
        if !hasTimer(id)
          if @fields.duration == null
            # if data.duration is null, countdown should be added.
            timer = new Timer stopclock_holder,
              "name": @fields.name
              "start_time": new Date(@fields.start_time)
              "running": @fields.running
              "id": @pk
              "stopped_at": @fields.stopped_at
              "no_refresh": @fields.no_refresh
              "auto_remove": @fields.auto_remove
          else
            timer = new Timer timer_holder,
              "name": @fields.name
              "duration": @fields.duration
              "start_time": new Date(@fields.start_time)
              "running": @fields.running
              "id": @pk
              "stopped_at": @fields.stopped_at
              "no_refresh": @fields.no_refresh
              "auto_remove": @fields.auto_remove

  addTimerId = (id) ->
    created_timer_items.push id

  sortTimers = ->
    items = jq(timer_holder).find(".timer-item")
    items.detach().sort (a, b) ->
      astts = jq(a).data "end-timestamp"
      bstts = jq(b).data "end-timestamp"
      return (astts > bstts) ? (astts > bstts) ? 1 : 0 : -1

    jq(timer_holder).append items

    items = jq(stopclock_holder).find(".timer-item")
    items.detach().sort (a, b) ->
      astts = jq(a).data "start-timestamp"
      bstts = jq(b).data "start-timestamp"
      return (astts > bstts) ? (astts > bstts) ? 1 : 0 : -1

    jq(stopclock_holder).append items


  onReceiveWS = (message) ->
    data = message[0]
    if !hasTimer(data.pk)
      if data.fields.duration == null
        # if data.duration is null, countdown should be added
        run_timer = new Timer stopclock_holder,
          "name": data.fields.name
          "start_time": new Date(data.fields.start_time)
          "running": data.fields.running
          "id": data.pk
          "stopped_at": data.fields.stopped_at
          "no_refresh": data.fields.no_refresh
          "auto_remove": data.fields.auto_remove
      else
        run_timer = new Timer timer_holder,
          "name": data.fields.name
          "duration": data.fields.duration
          "start_time": new Date(data.fields.start_time)
          "running": data.fields.running
          "id": data.pk
          "stopped_at": data.fields.stopped_at
          "no_refresh": data.fields.no_refresh
          "auto_remove": data.fields.auto_remove


  ws_generic.register "timers", onReceiveWS
  ge_refresh.register "timers", refreshFromServer

  jq(".add-timer").click ->
    jq.post "/homecontroller/timer/create",
      "name": jq(@).data("name")
      "duration": jq(@).data("duration")

  jq(".add-stopclock").click ->
    jq.post "/homecontroller/timer/create",
      "name": "Ajastin"


  refreshFromServer()
  setInterval refreshFromServer, options.update_interval

  @sortTimers = sortTimers
  @hasTimer = hasTimer
  @refreshFromServer = refreshFromServer
  @addTimerId = addTimerId
  return @


jq =>
  @timers = new Timers
    stopclock_holder: "#stopclock-holder"
    timer_holder: "#timer-holder"
