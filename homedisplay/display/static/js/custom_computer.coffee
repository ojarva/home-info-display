refreshCallback = ->
  setTimeout () ->
    jq(".navbar .refresh").removeClass "fa-spin"
  , 1500

jq ->
  ge_refresh.setRefreshCallback refreshCallback

  jq(".navbar-brand").on "click", ->
    content_switch.switchContent "#main-content"

  jq(".navbar .refresh").on "click", ->
    jq(@).addClass "fa-spin"
    ge_refresh.requestUpdate()
