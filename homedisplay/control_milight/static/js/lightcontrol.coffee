LightSlider = (elem) ->
  this_elem = jq elem
  group_id = this_elem.data("id")
  value = 0
  update_timeout = null

  updateBackend = ->
    if value > 95
      value = 100
      this_elem.slider "value", value

    jq.post "/homecontroller/lightcontrol/control/brightness/#{group_id}/#{value}"

  slider = this_elem.slider
    value: 0
    min: 0
    max: 100
    range: "max"
    slide: (event, ui) ->
      if update_timeout?
        update_timeout = clearTimeout update_timeout

      update_timeout = setTimeout updateBackend, 100
      value = ui.value

  return this

LightControl = ->

  color_map =
    "white": "valkoinen"
    "red": "punainen"
    "blue": "sininen"
  latest_data = null
  delayed_process = null

  initialize = (selector) ->
    jq.each jq(".brightness-slider"), ->
      LightSlider(this)

    jq.each jq(selector), ->
      jq(this).data "original-color", jq(this).css("background-color")
      jq(this).children().not(".active-mode").each ->
        jq(this).data "original-classes", jq(this).attr("class")


      jq(this).on "click", ->
        content_switch.userActivity()
        main_elem = jq this
        if main_elem.data "running"
          return

        main_elem.data "running", true
        command = main_elem.data "command"
        group = main_elem.data("group") or "0"
        source = main_elem.data "source"
        main_elem.animate
          backgroundColor: "#ffffff"
        , 250
        main_elem.children().not(".active-mode").removeClass().addClass("fa fa-spinner fa-spin")
        animate_completed = (icon) ->
          main_elem.data "running", false
          main_elem.children().not(".active-mode").removeClass().addClass("fa fa-" + icon)
          restore_classes = ->
            main_elem.children().not(".active-mode").each ->
              elem = jq this
              elem.removeClass().addClass elem.data("original-classes")

            main_elem.stop().animate
              backgroundColor: main_elem.data("original-color")
            , 1000

          setTimeout restore_classes, 2000


        url = "/homecontroller/lightcontrol/control/"
        if source
          url += "source/" + source + "/" + command
        else
          url += command + "/" + group
        jq.ajax
          url: url
          type: "POST"

          success: ->
            animate_completed "check"
          error: ->
            animate_completed "times"

  delayedProcessData = ->
    max_brightness = 0
    data = latest_data
    if data? and data.groups?
      jq.each data.groups, ->
        group_id = this.fields.group_id
        color = this.fields.color
        jq(".light-group-#{group_id}-name").html this.fields.description
        jq(".light-group-#{group_id}-brightness").html("#{this.fields.current_brightness}%").data("brightness", this.fields.current_brightness)

        jq(".brightness-slider-group-#{group_id}").slider "value", this.fields.current_brightness
        jq(".brightness-slider-group-#{group_id}").css "background-color", color

        color_elem = jq(".light-group-#{group_id}-color")
        if color_map[color]?
          color_elem.html color_map[color]

        if this.fields.on
          jq(".light-group-#{group_id}-color").html "<i class='fa fa-toggle-on'></i>"
        else
          jq(".light-group-#{group_id}-color").html "<i class='fa fa-toggle-off'></i>"

        max_brightness = Math.max max_brightness, this.fields.morning_light_level

        if this.fields.morning_light_level < 10
          jq(".lights-morning-auto-" + group_id).addClass("lights-morning-dim").removeClass("lights-morning-bright")
        else
          jq(".lights-morning-auto-" + group_id).addClass("lights-morning-bright").removeClass("lights-morning-dim")

      if max_brightness < 10
        jq(".lights-morning-auto").addClass("lights-morning-dim").removeClass("lights-morning-bright")
      else
        jq(".lights-morning-auto").addClass("lights-morning-bright").removeClass("lights-morning-dim")

    if data? and data.main_buttons?
      jq.each data.main_buttons, (key, value) ->
        if value
          jq(".lights-" + key).find(".active-mode").show()
        else
          jq(".lights-" + key).find(".active-mode").hide()

  processData = (data) ->
    # Usually there is multiple updates for this. Delay processing a bit.
    latest_data = data
    if delayed_process?
      delayed_process = clearTimeout delayed_process

    delayed_process = setTimeout delayedProcessData, 100


  update = ->
    jq.get "/homecontroller/lightcontrol/status", (data) ->
      processData data


  ws_generic.register "lightcontrol", processData
  ge_refresh.register "lightcontrol", update

  this.initialize = initialize
  this.update = update
  return this

obj = this
jq ->
  obj.light_control = new LightControl()
  light_control.initialize ".lightcontrol-btn"
  light_control.update()

  jq(".main-button-box .lights").on "click", ->
    content_switch.switchContent "#lightcontrol-modal"

  jq("#lightcontrol-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
