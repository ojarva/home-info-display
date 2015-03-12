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
    total_entries = data.length
    current_elem = jq(".transportation ul").slice(0, 1)
    items = 0
    jq.each data, ->
      # Loop over stops
      items += 1
      current_elem.append "<li><span class='line-number'>#{@line}:</span> <span class='departures' data-minimum-time='#{@minimum_time}'></span></li>"
      this_departures = current_elem.find("li .departures").last()
      departures_for_stop = 0
      jq.each @departures, ->
        # Loop over departures
        this_departures.append "<span class='auto-update-timestamp' data-timestamp='#{this}'><span class='minutes'></span><span class='seconds'></span></span> "
        departures_for_stop += 1
        if departures_for_stop > 1
          return false
      if items > total_entries / 2
        current_elem = jq(".transportation ul").slice(1, 2)

    updateTimestamps()

  update = ->
    jq.get "/homecontroller/transportation/get_json", (data) ->
      processData data

  update()
  update_interval = setInterval ->
    update()
  , FAST_UPDATE
  timestamp_update_interval = setInterval ->
    updateTimestamps()
  , 1000
  ws_generic.register("public-transportation", processData)

  return this

jq =>
  this.transportation = new Transportation()
