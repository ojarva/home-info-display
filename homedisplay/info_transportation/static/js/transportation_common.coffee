TransportationCommon = (show_first) ->
  clearEntries = ->
    jq(".transportation ul li").remove()

  updateTimestamps = () ->
    now = clock.getMoment()
    jq(".transportation .departures").each ->
      visible_departures = 0
      cutoff_covered = false
      jq(this).find(".auto-update-timestamp").each ->
        this_elem = jq this
        diff = moment(this_elem.data("timestamp")) - now
        diff /= 1000 # In seconds
        minimum_time = parseInt this_elem.parent().data("minimum-time") # in seconds
        if diff < minimum_time
          jq(this).hide "drop",
            duration: 900
            "direction": "left"
            complete: ->
              # Update next departure as first.
              next_departure = this_elem.parent().children().first()
              next_departure.hide().addClass("first-departure")
              this_elem.remove()
              next_departure.show "drop",
                "duration": 900
                "direction": "left"
          return true # continue

        if diff - minimum_time > 30 * 60
          if cutoff_covered
            # Not the first one that is over 30min
            this_elem.addClass "hide-too-long"
          else
            cutoff_covered = true
            this_elem.removeClass "hide-too-long"
        else
          this_elem.removeClass "hide-too-long"
        minutes_raw = Math.floor diff / 60

        seconds = ("00" + Math.floor(diff - (60 * minutes_raw))).substr(-2, 2)
        this_elem.find(".minutes").html minutes_raw
        this_elem.find(".seconds").html ":#{seconds}"

      this_elem = jq this
      this_elem.find(".auto-update-timestamp").first().addClass("first-departure")
      this_elem.find(".auto-update-timestamp").slice(show_first).hide()
      this_elem.find(".auto-update-timestamp").filter(".hide-too-long").hide()
      this_elem.find(".seconds").first().show()
      this_elem.find(".seconds").slice(1).hide()


  this.clearEntries = clearEntries
  this.updateTimestamps = updateTimestamps
  return this

this.TransportationCommon = TransportationCommon
