WifiInfo = ->
  hostname_database = {}
  update_timeout = null
  elem = jq "#wifi-clients"
  initialized = false

  initialize = ->
    if initialized
      return
    initialized = true
    jq.get "/homecontroller/internet_connection/wifi/info", (data) ->
      elem.find(".ssid").html data.ssid
      elem.find(".passphrase").html data.passphrase
      jq("#wifi-qr").qrcode
        "text": "WIFI:S:#{data.ssid};T:WPA;P:#{data.passphrase};;"
        "background": "white"
        "render": "div"
        "size": 600
      return

  clearEntries = ->
    elem.children().remove()

  updateUnifi = (data) ->
    clearEntries()
    update_timeout = clearTimeout update_timeout
    update_timeout = setTimeout clearEntries, 60 * 1000
    jq.each data.devices, ->
      hostname_from_lease = hostname_database[@mac]
      if hostname_from_lease?
        hostname = "<span class='hostname'>#{hostname_from_lease}</span>"
      else
        hostname = ""
      elem.append """<div class='wifi-client'>
        <div class='device-info'>
          <span class='mac'>#{@mac}</span>#{hostname}
        </div>
        <div class='generic-info'>
          <span class='last-seen'>#{@last_seen}</span>
          <span class='rssi-container'>
            <span class='label'>rssi:</span>
            <span class='rssi'>#{@rssi}</span><span class='unit'>dBm</span>
          </span>
          <span class='bandwidth'>#{@bandwidth_in}/#{@bandwidth_out}</span><span class='label'>Mbit/s</span>
        </div>
      </div>"""

  updateMacs = (data) ->
    jq.each data.devices, ->
      hostname_database[@mac] = @hostname
    return hostname_database

  ws_generic.multiRegister "unifi-status", "unifi-status-main", updateUnifi
  ws_generic.multiRegister "dhcp-leases", "unifi-status-main", updateMacs

  initialize()
  return @

jq =>
  @wifi_info = new WifiInfo()

  jq(".open-wifi-settings").on "click", ->
    content_switch.switchContent "#wifi-settings"

  jq("#wifi-settings .close").on "click", ->
    content_switch.switchContent "#main-content"
