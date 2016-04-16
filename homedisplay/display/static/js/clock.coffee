ClockCalendar = (options) ->
  options = options or {}
  options.update_interval = options.update_interval or 1000
  options.sync_interval = options.sync_interval or FAST_UPDATE
  update_interval = null
  sync_interval = null
  clock_offset = 0

  getOffset = ->
    return clock_offset


  processOffset = (timestamp) ->
    server_timestamp = parseInt timestamp
    if server_timestamp < 1425731077393
      console.error "Invalid timestamp from server"
      return

    clock_offset = -1 * parseInt(new Date(server_timestamp) - new Date()) # In milliseconds


  updateOffset = ->
    jq.get "/homecontroller/timer/current_time", (timestamp) ->
      processOffset timestamp


  getMoment = ->
    # Get moment with current offset
    return moment().subtract(getOffset()).tz("Europe/Helsinki")


  getDate = ->
    # Get javascript date with current offset
    return new Date(new Date() - getOffset())


  update = ->
    days = new Array("su", "ma", "ti", "ke", "to", "pe", "la")
    currentTime = getMoment()
    jq(".calendar").html currentTime.format("dd D.M.")
    currentHours = currentTime.getHours()
    currentMinutes = currentTime.getMinutes()
    currentSeconds = currentTime.getSeconds()
    currentHoursPadded = ("0#{currentHours}").substr(-2, 2)
    currentMinutes = ("0#{currentMinutes}").substr(-2, 2)
    currentSeconds = ("0#{currentSeconds}").substr(-2, 2)
    jq(".clock").html currentTime.format("H:mm:ss")
    jq(".clock-hours").html currentTime.format("H")
    jq(".clock-minutes").html currentTime.format("mm")


  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval

    if sync_interval?
      sync_interval = clearInterval sync_interval


  startInterval = ->
    stopInterval()
    update()
    updateOffset()
    update_interval = setInterval update, options.update_interval
    sync_interval = setInterval updateOffset, options.sync_interval


  ge_refresh.register "clock-sync", updateOffset
  ws_generic.multiRegister "clock-sync", "clock-sync-main", processOffset

  @updateOffset = updateOffset
  @getOffset = getOffset
  @update = update
  @startInterval = startInterval
  @stopInterval = stopInterval
  @getMoment = getMoment
  @getDate = getDate
  return @


TimedRefresh = ->
  last_run_on_hour = clock.getDate().getHours()
  last_run_on_day = clock.getDate().getDay() # This is not unique, but if delay between checks is more than a month, something is seriously wrong.
  intervals = {}

  register = (key, interval, callback) ->
    if not intervals[interval]?
      intervals[interval] = {}

    intervals[interval][key] = callback
    debug.log "Registered interval #{interval} for key #{key}"


  deRegister = (key, interval) ->
    if intervals[interval]?
      delete intervals[interval][key]

  executeCallbacks = (interval) ->
    if not intervals[interval]?
      debug.warn "Interval #{interval} does not exist"
      return

    for key of intervals[interval]
      intervals[interval][key]()

  runIntervals = ->
    now = clock.getDate()
    hour = now.getHours()
    day = now.getDay()
    if hour != last_run_on_hour
      last_run_on_hour = hour
      executeCallbacks "hourly"

    if day != last_run_on_day
      last_run_on_day = day
      executeCallbacks "daily"

  # Missing intervals by 5 seconds is not optimal, but good enough.
  setInterval runIntervals, 5000

  @register = register
  @deRegister = deRegister
  @executeCallbacks = executeCallbacks
  return @

jq =>
  moment.tz.add("Europe/Helsinki|HMT EET EEST|-1D.N -20 -30|0121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121212121|-1WuND.N OULD.N 1dA0 1xGq0 1cM0 1cM0 1cM0 1cN0 1cM0 1cM0 1fA0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1fA0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1cM0 1fA0 1o00 11A0 1o00 11A0 1o00 11A0 1qM0 WM0 1qM0 WM0 1qM0 11A0 1o00 11A0 1o00 11A0 1qM0 WM0 1qM0 WM0 1qM0 WM0 1qM0 11A0 1o00 11A0 1o00 11A0 1qM0 WM0 1qM0 WM0 1qM0 11A0 1o00 11A0 1o00 11A0 1o00 11A0 1qM0 WM0 1qM0 WM0 1qM0 11A0 1o00 11A0 1o00 11A0 1qM0 WM0 1qM0 WM0 1qM0 11A0 1o00 11A0 1o00 11A0 1o00 11A0 1qM0 WM0 1qM0 WM0 1qM0 11A0 1o00 11A0 1o00 11A0 1qM0 WM0 1qM0 WM0 1qM0 WM0 1qM0 11A0 1o00 11A0 1o00|12e5")
  @clock = new ClockCalendar()
  @clock.startInterval()
  @ge_intervals = new TimedRefresh()
