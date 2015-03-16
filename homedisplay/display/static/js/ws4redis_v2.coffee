@WS4Redis = (options, $) ->
  opts = null
  ws = null
  deferred = null
  timer = null
  timer_interval = 0
  closed = false
  heartbeat_interval = null
  missed_heartbeats = 0
  disconnected_since = null

  if options.uri == undefined
    throw new Error 'No Websocket URI in options'

  if $ == undefined
    $ = jQuery

  opts = jq.extend
    heartbeat_msg: null
  , options

  connect = (uri) ->
    try
      deferred = jq.Deferred()
      ws = new WebSocket uri
      ws.onopen = on_open
      ws.onmessage = on_message
      ws.onerror = on_error
      ws.onclose = on_close
      timer = null
    catch err
      deferred.reject new Error(err)

  send_heartbeat = ->
    try
      missed_heartbeats++
      if missed_heartbeats > 3
        throw new Error "Too many missed heartbeats."

      ws.send opts.heartbeat_msg
    catch e
      heartbeat_interval = clearInterval heartbeat_interval
      console.warn "Closing connection. Reason: #{e.message}"
      ws.close()

  on_open = ->
    console.log "Connected to #{ws.url}"
    if debug and debug.log
      debug.log "Connected to websocket"

    if internet_disconnected?
      internet_disconnected.connected "websocket"

    timer_interval = 500
    deferred.resolve()
    if opts.heartbeat_msg and heartbeat_interval == null
      missed_heartbeats = 0
      heartbeat_interval = setInterval send_heartbeat, 5000

  on_close = (evt) ->
    if closed
      return

    console.log "Connection to #{ws.url} closed!"

    if internet_disconnected?
      internet_disconnected.disconnected "websocket"

    if !timer
      # try to reconnect
      timer = setTimeout ->
        connect ws.url
      , timer_interval
      timer_interval = Math.min timer_interval + 500, 15000

  on_error = (evt) ->
    console.error "Websocket connection is broken!"
    if debug and debug.error
      debug.error "Websocket disconnected"
    deferred.reject new Error(evt)

  on_message = (evt) ->
    if opts.heartbeat_msg and evt.data == opts.heartbeat_msg
      # reset the counter for missed heartbeats
      missed_heartbeats = 0
    else if typeof opts.receive_message == 'function'
      return opts.receive_message evt.data

  send_message = (message) ->
    ws.send message

  close = ->
    closed = true
    if heartbeat_interval?
      heartbeat_interval = clearInterval heartbeat_interval
    ws.close()

  connect opts.uri

  @close = close
  @send_message = send_message
  return @
