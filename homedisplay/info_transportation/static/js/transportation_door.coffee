Transportation = () ->
  update_interval = null
  timestamp_update_interval = null

  show_first = 2
  transportation_common = new TransportationCommon show_first

  processData = (data) ->
    transportation_common.clearEntries()
    total_entries = data.length
    current_elem = jq(".transportation ul").slice 0, 1
    items = 0
    jq.each data, ->
      # Loop over stops
      items += 1
      current_elem.append "<li><span class='line-number'>#{@line}:</span> <span class='departures' data-minimum-time='#{@minimum_time}'></span></li>"
      departures = current_elem.find("li .departures").last()
      departures_for_stop = 0
      jq.each @departures, ->
        # Loop over departures
        departures.append "<span class='auto-update-timestamp' data-timestamp='#{@}'><span class='minutes'></span><span class='seconds'></span></span> "
        departures_for_stop += 1
      if items > total_entries / 2
        current_elem = jq(".transportation ul").slice 1, 2

    transportation_common.updateTimestamps()

  update = ->
    jq.get "/homecontroller/transportation/get_json?" + (+ new Date()), (data) ->
      processData data

  update()
  update_interval = setInterval update, FAST_UPDATE
  timestamp_update_interval = setInterval transportation_common.updateTimestamps, 1000
  ws_generic.register "public-transportation", processData

  return @

jq =>
  setTimeout =>
    @transportation = new Transportation()
  , 3000
