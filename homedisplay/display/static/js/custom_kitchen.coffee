ExtContent = ->
  receivedPage = (page) ->
    jq("#ext-content-frame iframe").attr "src", page
    jq("#main-open-ext-content-frame").slideDown()
    jq("#main-open-ext-content-frame").trigger "click"

  ws_generic.register "open-ext-page", receivedPage

jq ->
  ext_content = new ExtContent()

  height = jq(window).height()
  jq(".content-box").css
    "height": height
  .css
    "min-height": height

  jq("#ext-content-frame .close").on "click", ->
    content_switch.switchContent "#main-content"

  jq(".open-ext-content-frame").on "click", ->
    content_switch.switchContent "#ext-content-frame", false
