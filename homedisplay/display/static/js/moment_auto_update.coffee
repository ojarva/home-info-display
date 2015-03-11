MomentAutoUpdate = (options) ->
  options = options || {}
  options.update_interval = options.update_interval || 15000
  options.selector = options.selector || ".auto-fromnow-update"

  update_interval = null

  update = ->
    elem = jq options.selector
    jq.each elem, ->
      ts = jq(this).data("timestamp")
      jq(this).html(moment(ts).fromNowSynced())

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
  return this

moment_auto_update = null

jq ->
  moment_auto_update = new MomentAutoUpdate()
  moment_auto_update.startInterval()
