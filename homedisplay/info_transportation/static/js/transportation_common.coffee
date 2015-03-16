TransportationCommon = (show_first) ->
  clearEntries = ->
    jq(".transportation ul li").remove()

  updateTimestamps = () ->
    now = clock.getMoment()
    jq(".transportation .departures").each ->
      visible_departures = 0
      cutoff_covered = false
      jq(@).find(".auto-update-timestamp").each ->
        auto_update_elem = jq @
        diff = moment(auto_update_elem.data("timestamp")) - now
        diff /= 1000 # In seconds
        minimum_time = parseInt auto_update_elem.parent().data("minimum-time") # in seconds
        if diff < minimum_time
          jq(@).hide "drop",
            duration: 900
            "direction": "left"
            complete: ->
              # Update next departure as first.
              next_departure = auto_update_elem.parent().children().first()
              next_departure.hide().addClass("first-departure")
              auto_update_elem.remove()
              next_departure.show "drop",
                "duration": 900
                "direction": "left"
          return true # continue

        if diff - minimum_time > 30 * 60
          if cutoff_covered
            # Not the first one that is over 30min
            auto_update_elem.addClass "hide-too-long"
          else
            cutoff_covered = true
            auto_update_elem.removeClass "hide-too-long"
        else
          auto_update_elem.removeClass "hide-too-long"
        minutes_raw = Math.floor diff / 60

        seconds = ("00" + Math.floor(diff - (60 * minutes_raw))).substr(-2, 2)
        auto_update_elem.find(".minutes").html minutes_raw
        auto_update_elem.find(".seconds").html ":#{seconds}"

      departures_list = jq @
      departures_list.find(".auto-update-timestamp").first().addClass("first-departure")
      departures_list.find(".auto-update-timestamp").slice(show_first).hide()
      departures_list.find(".auto-update-timestamp").filter(".hide-too-long").hide()
      departures_list.find(".seconds").first().show()
      departures_list.find(".seconds").slice(1).hide()


  @clearEntries = clearEntries
  @updateTimestamps = updateTimestamps
  return @

@TransportationCommon = TransportationCommon
