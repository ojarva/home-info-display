CustomTimer = (options) ->
  options = options or {}
  duration_elem = jq options.duration_elem
  modal_elem = jq options.modal_elem
  time_spec =
    "h_s": 0
    "h_l": 3
    "m_s": 3
    "m_l": 2
    "s_s": 5
    "s_l": 2

  clearLabels = ->
    jq(".custom-timer-labels").children().remove()
    jq(".timed-custom-timer-labels").children().remove()

  submitTimer = (name) ->
    c = duration_elem.data "content"
    seconds = parseInt(c.substr(0, 3)) * 3600 + parseInt(c.substr(3, 2)) * 60 + parseInt(c.substr(5, 2))
    if seconds == 0
      # If no time is set, try getting duration for fixed-length items
      seconds = jq(@).data "duration"

    if seconds?
      jq.post "/homecontroller/timer/create",
        name: name
        duration: seconds

    modal_elem.find(".close").click()


  processLabels = (data) ->
    clearLabels()
    jq.each data.labels, ->
      jq(".custom-timer-labels").append "<div class='timer-description-button animate-click'>#{@}</div>"

    jq.each data.timed_labels, ->
      jq(".timed-custom-timer-labels").append "<div class='timer-description-button animate-click' data-duration='#{@duration}'>#{@label}</div>"

    modal_elem.find(".timer-description-button").on "click", ->
      content_switch.userActivity()
      name = jq(@).html()
      submitTimer(name)

  updateLabels = ->
    jq.get "/homecontroller/timer/get_labels", (data) ->
      processLabels data

  zeroPad = (num, places) ->
    zero = places - num.toString().length + 1
    return Array(+(zero > 0 and zero)).join("0") + num

  getTimeField = (content, field) ->
    d = content.substring(time_spec["#{field}_s"], time_spec["#{field}_s"] + time_spec["#{field}_l"])
    return d

  setTimeField = (content, field, data) ->
    index_start = time_spec["#{field}_s"]
    length = time_spec["#{field}_l"]
    d = content.substring(0, index_start) + data + content.substring(index_start + length)
    return d

  processButton = (content) ->
    current_content = duration_elem.data "content"
    data = parseInt content.substring(0, content.length - 1)
    field = content.substring(content.length - 1)
    field_data = parseInt getTimeField(current_content, field)
    field_data += data
    if field_data < 0
      hours_field = parseInt getTimeField(current_content, "h")
      minutes_field = parseInt getTimeField(current_content, "m")
      if field == "s"
        if minutes_field == 0 and hours_field > 0
          # Take 1h to minutes field.
          hours_field -= 1
          current_content = setTimeField current_content, "h", zeroPad(hours_field, time_spec.h_l)
          minutes_field += 60

        if minutes_field > 0
          # Take 1 minute to seconds field.
          minutes_field -= 1
          field_data += 60
          current_content = setTimeField current_content, "m", zeroPad(minutes_field, time_spec.m_l)
        else
          field_data = 0

      else if field == "m"
        if hours_field > 0
          # Take 1 hour to minutes field.
          hours_field -= 1
          field_data += 60
          current_content = setTimeField current_content, "h", zeroPad(hours_field, time_spec.h_l)
        else
          field_data = 0
      else
        field_data = 0

    if (field == "s" or field == "m") and field_data >= 60
      if field == "s"
        minutes_field = parseInt getTimeField(current_content, "m")
        minutes_field += 1
        field_data -= 60
        if minutes_field >= 60
          minutes_field -= 60
          hours_field = parseInt getTimeField(current_content, "h")
          hours_field += 1
          current_content = setTimeField current_content, "h", zeroPad(hours_field, time_spec.h_l)

        current_content = setTimeField current_content, "m", zeroPad(minutes_field, time_spec.m_l)

      if field == "m"
        field_data -= 60
        hours_field = parseInt getTimeField(current_content, "h")
        hours_field += 1
        current_content = setTimeField current_content, "h", zeroPad(hours_field, time_spec.h_l)

    field_data = zeroPad field_data, time_spec["#{field}_l"]
    current_content = setTimeField current_content, field, field_data

    duration_elem.data "content", current_content
    c = current_content
    duration_elem.html c.substr(0, 3) + ":" + c.substr(3, 2) + ":" + c.substr(5, 2)


  closeCustomTimer = ->
    c = "0000000"
    duration_elem.data "content", c
    duration_elem.html c.substr(0, 3) + ":" + c.substr(3, 2) + ":" + c.substr(5, 2)

    content_switch.switchContent "#main-content"

  showCustomTimer = ->
    content_switch.switchContent "#add-custom-timer"

  modal_elem.find(".add-timer-button").on "click", ->
    content_switch.userActivity()
    content = jq(@).data("content").trim()
    processButton content

  jq(".add-custom-timer-plus").on "click", ->
    showCustomTimer()

  modal_elem.find(".close").on "click", ->
    closeCustomTimer()

  updateLabels()
  ge_refresh.register "timer-labels", updateLabels
  ws_generic.register "timer-labels", processLabels

  @showCustomTimer = showCustomTimer
  @closeCustomTimer = closeCustomTimer
  @submitTimer = submitTimer
  @processButton = processButton
  @setTimeField = setTimeField
  @getTimeField = getTimeField

  return @

jq =>
  @custom_timer = new CustomTimer
    duration_elem: "#custom-timer-duration"
    modal_elem: "#add-custom-timer"
