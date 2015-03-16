ExtContent = ->
  id = null

  receivedPage = (data, show = true) ->
    url = data.url
    id = data.id
    jq("#ext-content-frame iframe").attr "src", url
    .data "page-id", id
    # Show "open ext page dialog" button
    if show
      jq("#main-open-ext-content-frame").slideDown().trigger("click")

  ws_generic.register "open-ext-page", receivedPage

  gotoBefore = ->
    if id?
      jq.get "/homecontroller/ext_pages/pull/page/before/#{id}", (data) ->
        receivedPage data, false

  gotoAfter = ->
    if id?
      jq.get "/homecontroller/ext_pages/pull/page/after/#{id}", (data) ->
        receivedPage data, false

  gotoLatest = ->
    jq.get "/homecontroller/ext_pages/pull/page/latest", (data) ->
      if data.id
        receivedPage data, false

  @gotoBefore = gotoBefore
  @gotoAfter = gotoAfter
  @gotoLatest = gotoLatest
  return @

jq =>
  obj = @
  obj.ext_content = new ExtContent()
  obj.ext_content.gotoLatest()

  jq("#ext-content-frame .close").on "click", ->
    content_switch.switchContent "#main-content"

  jq(".open-ext-content-frame").on "click", ->
    content_switch.switchContent "#ext-content-frame", false

  jq("#ext-content-frame .after").on "click", ->
    obj.ext_content.gotoAfter()

  jq("#ext-content-frame .before").on "click", ->
    obj.ext_content.gotoBefore()

  jq("#ext-content-frame .latest").on "click", ->
    obj.ext_content.gotoLatest()
