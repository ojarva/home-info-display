FrameHandler = () ->
  watchdog_last_update = + new Date()
  last_reload_time = + new Date()

  setInterval ->
    timestamp = + new Date()
    if watchdog_last_update < timestamp - 10000
      if timestamp - last_reload_time < 10000
        console.debug "No need to try reloading yet"
        return
      console.warn "Watchdog timer expired"
      elem = jq("#content-frame")
      src = elem.attr("src").split("?")[0] + "?" + timestamp
      elem.attr("src", src)
      last_reload_time = timestamp
  , 2500

  window.addEventListener "message", (e) ->
    watchdog_last_update = e.data
  , false
frame_handler = null;

jq ->
  frame_handler = new FrameHandler()
