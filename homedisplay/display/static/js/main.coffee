moment.locale("fi")

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
    jq("html, body").animate({ scrollTop: 0 }, "fast") # Always scroll to top.
    jq("#navbar").collapse("hide") # Hide menu, if visible
    if elem != "#main-content" and set_timeout
      switch_visible_content_currently_active = elem
      switch_visible_content_timeout = setTimeout mainContent, 60 * 1000
      jq(elem).show()

  userAction = ->
    if switch_visible_content_currently_active != "#main-content"
      resetSwitchToMain()

  this.switchContent = switchContent
  this.mainContent = mainContent
  this.userActivity = userAction
  return this

obj = this

jq ->
  obj.content_switch = new ContentSwitch()
  jq(".animate-click").each ->
    jq(this).data "original-bg-color", jq(this).css("background-color")

  jq(".animate-click").on "click", ->
    jq(this).stop(true).css
      "background-color": jq(this).data "original-bg-color"
    .effect "highlight",
      color: "#ffffff"
      500

  jq("body").on "click", ->
    obj.content_switch.userActivity()
