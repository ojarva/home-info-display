WifiInfo = ->
  initialize = ->
    # This shouldn't be called more than once
    jq.get "/homecontroller/internet_connection/wifi/info", (data) ->
      elem = jq ".wifi-info"
      elem.find(".ssid").html data.ssid
      elem.find(".passphrase").html data.passphrase
      jq("#wifi-qr").qrcode
        "text": "WIFI:S:" + data.ssid + ";T:WPA;P:" + data.passphrase + ";;"
        "background": "white"
        "render": "div"
        "size": 600
      return

  updateUnifi = (data) ->
    elem = jq "#wifi-clients"
    elem.children().remove()
    jq.each data.devices, ->
      elem.append "<div class='wifi-client'><span class='mac'>" + this.mac + "</span> <span class='last-seen'>" + this.last_seen + "</span> <span class='label'>rssi:</span> <span class='rssi'>" + this.rssi + "</span><span class='unit'>dBm</span> <span class='bandwidth'>" + this.current_bandwidth + "/" + this.maximum_bandwidth + "</span><span class='label'>Mbit/s</span></div>"

  ws_generic.multiRegister "unifi-status", "unifi-status-main", updateUnifi

  initialize()
  return this

wifi_info = null

jq ->
  wifi_info = new WifiInfo()

  jq(".main-button-box .open-wifi-settings").on "click", ->
    content_switch.switchContent "#wifi-settings"

  jq("#wifi-settings .close").on "click", ->
    content_switch.switchContent "#main-content"
