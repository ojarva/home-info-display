Transportation = () ->
  update_interval = null
  timestamp_update_interval = null

  show_first = 8 # Show first 8 departures
  transportation_common = new TransportationCommon show_first


  processData = (data) ->
    transportation_common.clearEntries()
    jq.each data, ->
      # Loop over stops
      jq(".transportation ul").append """<li>
        <i class='fa fa-li fa-2x fa-#{@icon} type-#{@type}'></i>
        <span class='line-number'>#{@line}:</span>
        <span class='departures' data-line="#{@type}-#{@line}" data-minimum-time='#{@minimum_time}'></span>
      </li>"""
      departures = jq(".transportation ul li .departures").filter("[data-line=\"#{@type}-#{@line}\"]")
      departures_for_stop = 0
      jq.each @departures, ->
        if @.realtime
          extra_open = "<u>"
          extra_close = "</u>"
        else
          extra_open = extra_close = ""
        departures.append "<span class='auto-update-timestamp transportation-departure' data-timestamp='#{@.timestamp}' data-departure-id='#{@departure_id}'>#{extra_open}<span class='minutes'></span><span class='seconds'></span>#{extra_close}</span> "
        departures_for_stop += 1
        if departures_for_stop > 7
          return false

    jq(".transportation .transportation-departure").on "click", ->
      departure_id = jq(@).data("departure-id")
      fetchDeparturesForLine departure_id

    transportation_common.updateTimestamps()

  fetchDeparturesForLine = (departure_id) ->
    elems = jq.find(".line-departures")
    for elem in elems
      jq(elem).html """<h1>Ladataan <i class="fa fa-spin fa-spinner"></i></h1>"""
    jq.get "/homecontroller/transportation/data/line/#{departure_id}", (data) ->
      processLineDepartures data
    content_switch.switchContent("#transportation-dialog")

  processLineDepartures = (data) ->
    elems = jq.find(".line-departures")
    if not data? or data.length == 0
      line = "?"
    else
      line = data[0].line
    html = """
      <h1>Lähdöt: #{line}</h1>

      <table class="table table-striped">
      <tbody>
    """
    if not data? or data.length == 0
      html += """<tr><td colspan="3">Ei pysäkkejä</td></tr>"""
    for dep in data
      diff_from_schedule = ""
      if dep.rtime?
        rtime = moment(dep.rtime)
        time_info = "<u>" + moment(dep.rtime).format("H:mm:ss") + "</u>"
        time = moment(dep.time)
        diff = (rtime - time) / 1000
        minutes = Math.round(diff / 60 * 10) / 10
        if diff < -10
          diff_from_schedule = "etuajassa #{Math.abs(diff)}s"
        else if diff < 20
          diff_from_schedule = "ajallaan"
        else if diff < 60
          diff_from_schedule = "myöhässä #{diff}s"
        else
          diff_from_schedule = "myöhässä #{minutes}min"
      else
        time_info = moment(dep.time).format("H:mm:ss")


      html += """<tr><td>#{time_info}</td><td>#{diff_from_schedule}</td><td>#{dep.stopname}</td></tr>"""
    html += "</tbody></table>"
    for elem in elems
      jq(elem).html html

  update = ->
    jq.get "/homecontroller/transportation/get_json", (data) ->
      processData data
    jq.get "/homecontroller/transportation/poikkeustiedotteet", (data) ->
      processPoikkeusinfo data

  processPoikkeusinfo = (data) ->
    console.log data
    html = """<ul>"""
    if not data? or data.length == 0
      html += "<li>Ei poikkeusinfoja</li>"
    else
      for p in data
        html += "<li>#{p.info.text}</li>"
    html += """</ul>"""
    el = jq(".poikkeustiedotteet-data").html html
    return

  startInterval = ->
    stopInterval()
    update()
    update_interval = setInterval update, FAST_UPDATE
    timestamp_update_interval = setInterval transportation_common.updateTimestamps, 1000
    ws_generic.register "public-transportation", processData
    ge_refresh.register "public-transportation", update
    ws_generic.register "poikkeusinfo", processPoikkeusinfo

  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval

    if timestamp_update_interval?
      timestamp_update_interval = clearInterval timestamp_update_interval

    ws_generic.deRegister "public-transportation"
    ge_refresh.deRegister "public-transportation"
    ws_generic.deRegister "poikkeusinfo"

  @startInterval = startInterval
  @stopInterval = stopInterval
  @update = update
  return @

jq =>
  @transportation = new Transportation()
  @transportation.startInterval()


  jq(".open-transportation-dialog").on "click", ->
      content_switch.switchContent "#transportation-dialog"

    jq("#transportation-dialog .close").on "click", ->
      content_switch.switchContent "#main-content"
