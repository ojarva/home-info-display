moment.locale("fi")

# RFC1422-compliant Javascript UUID function. Generates a UUID from a random
# number (which means it might not be entirely unique, though it should be
# good enough for many uses). See http://stackoverflow.com/questions/105034
# Copied from https://gist.github.com/bmc/1893440
uuid = ->
  'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) ->
    r = Math.random() * 16 | 0
    v = if c is 'x' then r else (r & 0x3|0x8)
    v.toString(16)
  )

Logger = ->
  # Adapted from http://stackoverflow.com/a/1215400/592174
  old_console_log = console.log
  old_console_debug = console.debug

  @enableLogger = ->
    window["console"]["log"] = old_console_log
    window["console"]["debug"] = old_console_debug

  @disableLogger = ->
    window["console"]["log"] = ->
      return
    window["console"]["debug"] = ->
      return

  return @

ContentSwitch = ->

  switch_visible_content_timeout = null
  switch_visible_content_currently_active = "#main-content"

  mainContent = ->
    jq(switch_visible_content_currently_active).find(".close").trigger("click")
    if switch_visible_content_timeout?
      switch_visible_content_timeout = clearTimeout switch_visible_content_timeout

  resetSwitchToMain = ->
    if switch_visible_content_timeout?
      switch_visible_content_timeout = clearTimeout switch_visible_content_timeout
    switch_visible_content_timeout = setTimeout mainContent, 60 * 1000

  switchContent = (elem, set_timeout = true) ->
    if switch_visible_content_timeout?
      switch_visible_content_timeout = clearTimeout switch_visible_content_timeout

    jq(".content-box").hide() # Hide all content boxes
    jq("html, body").animate
      scrollTop: 0
    , "fast" # Always scroll to top.
    jq("#navbar").collapse "hide" # Hide menu, if visible
    if elem != "#main-content"
      if set_timeout
        switch_visible_content_timeout = setTimeout mainContent, 60 * 1000
      switch_visible_content_currently_active = elem
      jq(elem).show()

  userAction = ->
    if switch_visible_content_currently_active != "#main-content"
      resetSwitchToMain()

  @switchContent = switchContent
  @mainContent = mainContent
  @userActivity = userAction
  return @

jq =>
  @content_switch = new ContentSwitch()
  @logger = new Logger()

  obj = @

  jq(".animate-click").each ->
    jq(@).data "original-bg-color", jq(@).css("background-color")

  jq(".animate-click").on "click", ->
    jq(@).stop(true).css
      "background-color": jq(@).data "original-bg-color"
    .effect "highlight",
      color: "#ffffff"
      500

  jq("body").on "click", ->
    obj.content_switch.userActivity()
