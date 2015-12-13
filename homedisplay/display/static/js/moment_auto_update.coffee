TimerAutoUpdate = (options) ->
  options = options or {}
  options.update_interval = options.update_interval or 1000
  options.selector = options.selector or ".auto-timer-update"

  update_interval = null

  update = ->
    now = clock.getMoment()
    elem = jq options.selector
    jq.each elem, ->
      ts = moment(jq(@).data "timestamp")
      if now > ts
        d = now - ts
        neg = false
      else
        d = ts - now
        neg = true
      d = moment(d)
      d.subtract(d.utcOffset(), "minutes")
      if neg
        jq(@).html d.format("-H:mm:ss")
      else
        jq(@).html d.format("H:mm:ss")

  startInterval = ->
    stopInterval()
    update()
    update_interval = setInterval ->
      update()
    , options.update_interval

  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval

  @startInterval = startInterval
  @stopInterval = stopInterval
  @update = update
  return @

MomentAutoUpdate = (options) ->
  options = options or {}
  options.update_interval = options.update_interval or 15000
  options.selector = options.selector or ".auto-fromnow-update"

  update_interval = null

  update = ->
    elem = jq options.selector
    jq.each elem, ->
      ts = jq(@).data "timestamp"
      jq(@).html moment(ts).fromNowSynced()

  startInterval = ->
    stopInterval()
    update()
    update_interval = setInterval ->
      update()
    , options.update_interval

  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval

  @startInterval = startInterval
  @stopInterval = stopInterval
  @update = update
  return @

jq =>
  @moment_auto_update = new MomentAutoUpdate()
  @moment_auto_update.startInterval()
  @timer_auto_update = new TimerAutoUpdate()
  @timer_auto_update.startInterval()
