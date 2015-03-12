Transportation = () ->
  update_interval = null
  timestamp_update_interval = null

  clearEntries = ->
    jq(".transportation ul li").remove()

  updateTimestamps = ->
    now = clock.getMoment()
    jq(".transportation .auto-update-timestamp").each ->
      diff = moment(jq(this).data("timestamp")) - now
      diff /= 1000
      if diff < parseInt(jq(this).parent().data("minimum-time"))
        jq(this).hide "drop",
          duration: 900
          "direction": "left"
          complete: ->
            next_departure = jq(this).parent().children().first();
            next_departure.hide().addClass("first-departure");
            jq(this).remove();
            next_departure.show "drop",
              "duration": 900
              "direction": "left"

        return true # continue

      minutes_raw = Math.floor(diff / 60)

      seconds = ("00" + Math.floor(diff - (60 * minutes_raw))).substr(-2, 2)
      jq(this).find(".minutes").html minutes_raw
      jq(this).find(".seconds").html ":#{seconds}"

    jq(".transportation .departures .seconds").hide()
    jq(".transportation .departures").each ->
      jq(this).find(".auto-update-timestamp").first().addClass("first-departure")
      jq(this).find(".seconds").first().show()


  processData = (data) ->
    clearEntries()
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

    updateTimestamps()


  update = ->
    jq.get "/homecontroller/transportation/get_json", (data) ->
      processData(data)

  startInterval = ->
    stopInterval()
    update()
    update_interval = setInterval ->
      update()
    , FAST_UPDATE
    timestamp_update_interval = setInterval ->
      updateTimestamps()
    , 1000
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
