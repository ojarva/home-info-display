LightSlider = (elem) ->
  slider_elem = jq elem
  group_id = slider_elem.data "id"
  value = 0
  update_timeout = null

  updateBackend = ->
    if value > 95
      value = 100
      slider_elem.slider "value", value

    jq.post "/homecontroller/lightcontrol/control/brightness/#{group_id}/#{value}"

  slider = slider_elem.slider
    value: 0
    min: 0
    max: 100
    range: "max"
    slide: (event, ui) ->
      if update_timeout?
        update_timeout = clearTimeout update_timeout

      update_timeout = setTimeout updateBackend, 100
      value = ui.value

  return @

LightControl = ->

  color_map =
    "white": "valkoinen"
    "red": "punainen"
    "blue": "sininen"

  initialize = (selector) ->
    jq.each jq(".brightness-slider"), ->
      LightSlider @

    jq.each jq(selector), ->
      jq(@).data "original-color", jq(@).css("background-color")
      jq(@).children().not(".active-mode").each ->
        jq(@).data "original-classes", jq(@).attr("class")


      jq(@).on "click", ->
        content_switch.userActivity()
        main_elem = jq @
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
          main_elem.children().not(".active-mode").removeClass().addClass("fa fa-#{icon}")
          restore_classes = ->
            main_elem.children().not(".active-mode").each ->
              elem = jq @
              elem.removeClass().addClass elem.data("original-classes")

            main_elem.stop().animate
              backgroundColor: main_elem.data("original-color")
            , 1000

          setTimeout restore_classes, 2000


        url = "/homecontroller/lightcontrol/control/"
        if source?
          # Per source commands do not contain group ID
          url += "source/#{source}/#{command}"
        else
          url += "#{command}/#{group}"
        jq.ajax
          url: url
          type: "POST"

          success: ->
            animate_completed "check"
          error: ->
            animate_completed "times"

  processData = (data) ->
    if data? and data.groups?
      jq.each data.groups, ->
        group_id = @id
        color = @color
        jq(".light-group-#{group_id}-name").html @name
        jq ".light-group-#{group_id}-brightness"
        .html "#{@current_brightness}%"
        .data "brightness", @current_brightness

        jq(".brightness-slider-group-#{group_id}").slider "value", @current_brightness
        jq(".brightness-slider-group-#{group_id}").css "background-color", color

        color_elem = jq ".light-group-#{group_id}-color"
        if color_map[color]?
          color_elem.html color_map[color]

        if @on
          jq(".light-group-#{group_id}-on").html "<i class='fa fa-toggle-on'></i>"
        else
          jq(".light-group-#{group_id}-on").html "<i class='fa fa-toggle-off'></i>"

  update = ->
    jq.get "/homecontroller/lightcontrol/status", (data) ->
      processData data


  ws_generic.register "lightcontrol", processData
  ge_refresh.register "lightcontrol", update

  @initialize = initialize
  @update = update
  return @

jq =>
  @light_control = new LightControl()
  @light_control.initialize ".lightcontrol-btn"
  @light_control.update()

  jq(".main-button-box .lights").on "click", ->
    content_switch.switchContent "#lightcontrol-modal"

  jq("#lightcontrol-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
    jq("#lightcontrol-modal .timed-lightcontrol").removeClass "highlight"
