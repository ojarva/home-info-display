FrameHandler = () ->
  watchdog_last_update = + new Date()
  last_reload_time = + new Date()
  first_update_received = false

  setInterval ->
    timestamp = + new Date()
    if watchdog_last_update < timestamp - 10000
      if first_update_received
        if timestamp - last_reload_time < 10000
          console.debug "No need to try reloading yet"
          return
      else
        if timestamp - last_reload_time < 60000
          console.debug "No watchdog event received from frame. Do not reload yet."
          return
      console.warn "Watchdog timer expired"
      elem = jq("#content-frame")
      src = elem.attr("src").split("?")[0] + "?" + timestamp
      elem.attr("src", src)
      last_reload_time = timestamp
  , 2500

  window.addEventListener "message", (e) ->
    first_update_received = true
    watchdog_last_update = e.data
  , false
frame_handler = null;

jq ->
  frame_handler = new FrameHandler()
