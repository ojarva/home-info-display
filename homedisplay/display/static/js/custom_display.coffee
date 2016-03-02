# These are wall display specific hacks to prevent issues with not-too-well functioning touchscreen.
# Do not include in any other UI.

jq ->
  # Disabling right click menu is evil. However, Ubuntu&Chrome&touchscreen means problems when context menu is triggered.
#  jq("body").bind "contextmenu", ->
#    false
  setInterval ->
    window.getSelection().empty()
  , 1000

  height = jq(window).height()
  jq(".content-box").css
    "height": height
  .css
    "min-height": height

  jq('[data-toggle="popover"]').popover()
