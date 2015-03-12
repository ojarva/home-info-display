WifiInfo = ->
  hostname_database = {}

  initialize = ->
    # This shouldn't be called more than once
    jq.get "/homecontroller/internet_connection/wifi/info", (data) ->
      elem = jq ".wifi-info"
      elem.find(".ssid").html data.ssid
      elem.find(".passphrase").html data.passphrase
      jq("#wifi-qr").qrcode
        "text": "WIFI:S:#{data.ssid};T:WPA;P:#{data.passphrase};;"
        "background": "white"
        "render": "div"
        "size": 600
      return

  updateUnifi = (data) ->
    elem = jq "#wifi-clients"
    elem.children().remove()
    jq.each data.devices, ->
      hostname_from_lease = hostname_database[@mac]
      if hostname_from_lease?
        hostname = "<span class='hostname'>#{hostname_from_lease}</span>"
      else
        hostname = ""
      elem.append "<div class='wifi-client'><div class='device-info'><span class='mac'>#{@mac}</span>#{hostname}</div> <div class='generic-info'><span class='last-seen'>#{@last_seen}</span> <span class='rssi-container'><span class='label'>rssi:</span> <span class='rssi'>#{@rssi}</span><span class='unit'>dBm</span></span> <span class='bandwidth'>#{@bandwidth_in}/#{@bandwidth_out}</span><span class='label'>Mbit/s</span></div></div>"

  updateMacs = (data) ->
    elem = jq "#wifi-clients"
    jq.each data.devices, ->
      hostname_database[@mac] = @hostname
    return hostname_database

  ws_generic.multiRegister "unifi-status", "unifi-status-main", updateUnifi
  ws_generic.multiRegister "dhcp-leases", "unifi-status-main", updateMacs

  initialize()
  return this

jq =>
  this.wifi_info = new WifiInfo()

  jq(".main-button-box .open-wifi-settings").on "click", ->
    content_switch.switchContent "#wifi-settings"

  jq("#wifi-settings .close").on "click", ->
    content_switch.switchContent "#main-content"
