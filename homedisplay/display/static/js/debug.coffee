Debug = ->
  elem = jq "#debug-modal .debug-list"

  addItem = (text, itemClass) ->
    now = clock.getMoment()
    now_formatted = now.format "HH:mm:ss"
    now_fromNow = now.fromNowSynced()
    elem.prepend "<li><i class='#{itemClass} fa fa-fw fa-li fa-bug'></i> #{now_formatted} #{text} (<span class='auto-fromnow-update' data-timestamp='#{now}'>#{now_fromNow}</span>)</li>"
    elem.children().filter(":gt(50)").remove()

  log = (text) ->
    addItem text, ""

  warn = (text) ->
    addItem text, "warning-message"

  error = (text) ->
    addItem text, "error-message"

  @warn = warn
  @error = error
  @log = log
  return @

jq =>
  @debug = new Debug()

  jq(".main-button-box .debug-modal").on "click", ->
    content_switch.switchContent "#debug-modal"

  jq("#debug-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
