

jq ->
  jq.get "/homecontroller/internet_connection/wifi/info", (data) ->
    elem = jq(".wifi-info")
    elem.find(".ssid").html data.ssid
    elem.find(".passphrase").html data.passphrase
    jq("#wifi-qr").qrcode
      "text": "WIFI:S:" + data.ssid + ";T:WPA;P:" + data.passphrase + ";;"
      "background": "white"
      "render": "div"
      "size": 600
    return

  jq(".main-button-box .open-wifi-settings").on "click", ->
    content_switch.switchContent "#wifi-settings"

  jq("#wifi-settings .close").on "click", ->
    content_switch.switchContent "#main-content"
