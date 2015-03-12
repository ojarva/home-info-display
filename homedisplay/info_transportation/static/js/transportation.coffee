Transportation = () ->
  update_interval = null
  timestamp_update_interval = null

  show_first = 8 # Show first 8 departures
  transportation_common = new TransportationCommon(show_first)


  processData = (data) ->
    transportation_common.clearEntries()
    jq.each data, ->
      # Loop over stops
      jq(".transportation ul").append("<li><i class='fa fa-li fa-2x fa-#{@icon} type-#{@type}'></i> <span class='line-number'>#{@line}:</span> <span class='departures' data-minimum-time='#{@minimum_time}'></span></li>")
      this_departures = jq(".transportation ul li .departures").last()
      departures_for_stop = 0
      jq.each @departures, ->
        this_departures.append("<span class='auto-update-timestamp' data-timestamp='#{this}'><span class='minutes'></span><span class='seconds'></span></span> ")
        departures_for_stop += 1
        if departures_for_stop > 7
          return false

    transportation_common.updateTimestamps()


  update = ->
    jq.get "/homecontroller/transportation/get_json", (data) ->
      processData(data)

  startInterval = ->
    stopInterval()
    update()
    update_interval = setInterval update, FAST_UPDATE
    timestamp_update_interval = setInterval transportation_common.updateTimestamps, 1000
    ws_generic.register("public-transportation", processData)
    ge_refresh.register("public-transportation", update)

  stopInterval = ->
    if update_interval?
      update_interval = clearInterval(update_interval)

    if timestamp_update_interval?
      timestamp_update_interval = clearInterval(timestamp_update_interval)

    ws_generic.deRegister("public-transportation")
    ge_refresh.deRegister("public-transportation")

  @startInterval = startInterval
  @stopInterval = stopInterval
  @update = update
  return this

jq =>
  this.transportation = new Transportation()
  this.transportation.startInterval()
