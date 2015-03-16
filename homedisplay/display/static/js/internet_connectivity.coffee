InternetDisconnected = ->
  disconnectedBy = {}

  @connected = (requested_by) ->
    delete disconnectedBy[requested_by]
    if (k for own k of disconnectedBy).length == 0
      # No other caller has requested disconnected status
      content_switch.switchContent "#main-content"

  @disconnected = (requested_by) ->
    disconnectedBy[requested_by] = true

  return @


InternetConnectivity = ->
  status = (event) ->
    if navigator.onLine
      internet_disconnected.connected "online"
      console.log "Internet connection detected"
    else
      content_switch.switchContent "#disconnected"
      internet_disconnected.disconnected "online"
      console.error "Internet disconnected"

  window.addEventListener "online", status
  window.addEventListener "offline", status
  return @


jq =>
  @internet_disconnected = new InternetDisconnected()
  @internet_connectivity = new InternetConnectivity()
