OutdoorQuality = ->
  type_data =
    "particulateslt10um": {"limit": 50, "name": "10um"}
    "ozone": {"limit": 120, "name": "Otsoni"}
    "particulateslt2.5um": {"limit": 25, "name": "2.5um"}
    "sulphurdioxide": {"limit": 350, "name": "Rikkidioksidi"}
    "nitrogendioxide": {"limit": 200, "name": "Typpidioksidi"}

  data_timeout = null

  elem = jq ".outdoor-air-quality-content"

  clearData = ->
    elem.children().remove()
    jq(".outdoor-quality-warning").html ""
    if data_timeout?
      data_timeout = clearTimeout data_timeout

    data_timeout = setTimeout clearData, 90 * 60 * 1000

  receivedData = (message) ->
    clearData()
    max_percent = 0
    for own key, data of message
      value = data.value
      if key of type_data
        limit = type_data[key].limit
        name = type_data[key].name
        #console.debug "Limit value for #{key} is #{limit}. Latest measured value is #{value} at #{data.timestamp}"
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

        percent_of_limit = value / limit
        max_percent = Math.max(percent_of_limit, max_percent)

        elem.append """<span class="air-quality-item">
          <span class="type">#{name}</span>
          <span class="value">#{value}</span>
          <span class="unit">&mu;g/m<sup>3</sup></span>
          <span class="status"><i class="fa fa-#{icon} #{icon_class}"></i></span>
        </span>"""

    if max_percent > .75
      jq(".outdoor-quality-warning").html """<span class="error-message"><i class="fa fa-building"><i class="fa fa-child"> (#{Math.round(max_percent*100)}%)</span>"""
    return

  ws_generic.register "outside_air_quality", receivedData
  # TODO: ge_refresh

  @receivedData = receivedData
  return @

jq =>
  @outdoor_quality = new OutdoorQuality()
