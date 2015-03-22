OutdoorQuality = ->
  type_data = {
    "particulateslt10um": {"limit": 50, "name": "10um"},
    "ozone": {"limit": 120, "name": "Otsoni"},
    "particulateslt2.5um": {"limit": 25, "name": "2.5um"},
    "sulphurdioxide": {"limit": 350, "name": "Rikkidioksidi"},
    "nitrogendioxide": {"limit": 200, "name": "Typpidioksidi"},
  }

  elem = jq ".outdoor-air-quality-content"

  clearData = ->
    elem.children().remove()

  receivedData = (message) ->
    clearData()
    for own key, data of message
      value = data.value
      if key of type_data
        limit = type_data[key].limit
        name = type_data[key].name
        console.log "Limit value for #{key} is #{limit}. Latest measured value is #{value} at #{data.timestamp}"
        icon_class = ""
        if value > limit
          icon = "times"
          icon_class = "error-message"
        else if value > limit * .75
          icon = "times"
          icon_class = "warning-message"
        else if value > limit * .5
          icon = "check"
        else
          icon = "check"
          icon_class = "success-message"

        elem.append """<span class="air-quality-item">
          <span class="type">#{name}</span>
          <span class="value">#{value}</span>
          <span class="unit">&mu;g/m<sup>3</sup></span>
          <span class="status"><i class="fa fa-#{icon} #{icon_class}"></i></span>
        </span>"""
    return

  ws_generic.register "outside_air_quality", receivedData
  # TODO: ge_refresh

  @receivedData = receivedData
  return @

jq =>
  @outdoor_quality = new OutdoorQuality()
