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
