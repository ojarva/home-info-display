FrameHandler = () ->
  watchdog_last_update = + new Date()

  setInterval ->
    timestamp = + new Date()
    if watchdog_last_update < timestamp - 60000
      console.warn "Watchdog timer expired"
      elem = jq("#content-frame")
      src = elem.attr("src").split("?")[0] + "?#{timestamp}"
      elem.attr "src", src
  , 10000

  window.addEventListener "message", (e) ->
    watchdog_last_update = e.data
  , false

  return @

jq =>
  @frame_handler = new FrameHandler()
