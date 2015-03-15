refreshCallback = ->
  setTimeout () ->
    jq(".navbar .refresh").removeClass "fa-spin"
  , 1500

jq ->
  ge_refresh.setRefreshCallback refreshCallback

  jq(".navbar-brand").on "click", ->
    content_switch.switchContent "#main-content"

  jq(".navbar .refresh").on "click", ->
    jq(this).addClass "fa-spin"
    ge_refresh.requestUpdate()


  jq("#open-ext-page").submit ->
    jq.post "/homecontroller/display/push/ext_content",
      page: jq("#open-ext-page-url").val()
    , ->
      jq("#open-ext-page-url").val("")
    return false
