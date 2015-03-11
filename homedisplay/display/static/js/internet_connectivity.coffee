InternetConnectivity = ->
  console.log content_switch, content_switch.switchContent
  status = (event) ->
    # This is not executed on load. This might be important if this will ever show any status information
    if navigator.onLine
      content_switch.switchContent "#main-content"
      console.log "Connected"
    else
      content_switch.switchContent "#disconnected"
      console.error "Disconnected"

  window.addEventListener "online", status
  window.addEventListener "offline", status
  return this

internet_connectivity = null
jq ->
  internet_connectivity = new InternetConnectivity()
