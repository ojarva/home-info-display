DoorScreensaver = ->
  last_activity = new Date()
  hide_interval = null
  timeout = 2 * 60 * 1000

  startScreensaver = ->
    jq("#screensaver").slideDown()

  activity = ->
    jq("#screensaver").fadeOut("fast")
    last_activity = new Date()

  update = ->
    now = clock.getDate()
    hour = now.getHours()
    if hour > 21 or hour < 8
      # Active
      if new Date() - last_activity > timeout
        startScreensaver()
    else
      activity()

  hide_interval = setInterval ->
    update()
  , 60 * 1000

  jq("body").on "click", ->
    activity()

  @startScreensaver = startScreensaver
  @activity = activity
  return this

jq =>
  this.door_screensaver = new DoorScreensaver()
  height = jq(window).height()
  jq(".content-box").css
    "height": height
  .css
    "min-height": height
