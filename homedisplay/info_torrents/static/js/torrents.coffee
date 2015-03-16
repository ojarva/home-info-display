Torrents = ->
  update_interval = null


  clearItems = ->
    jq("#torrent-items tr").remove()

  processData = (items) ->
    clearItems()
    jq.each items, ->
      jq("#torrent-items").append """<tr data-hash='#{@hash}'>
        <td>#{@filename}</td>
        <td>#{filesize(@size)}</td>
        <td>#{@downloaded_percent}%</td>
        <td>#{@up_speed}</td>
        <td>#{@eta}</td>
        <td>#{@netdisk}</td>
        <td>
          <div class='action-button animate-click stripe-box' data-action='remove'><i data-original-classes='fa fa-trash' class='fa fa-trash'></i></div>
          <div class='action-button animate-click stripe-box' data-action='stop'><i data-original-classes='fa fa-stop' class='fa fa-stop'></i></div>
          <div class='action-button animate-click stripe-box' data-action='play'><i data-original-classes='fa fa-play' class='fa fa-play'></i></div>
        </td>
      </tr>"""

    jq("#torrent-items .action-button").on "click", ->
      content_switch.userActivity()
      command = jq(@).data "action"
      hash = jq(@).parent().parent().data "hash"
      jq(@).find("i").removeClass().addClass "fa fa-spin fa-spinner"
      # No need to remove spinner, as whole table will be redrawn.
      jq.post "/homecontroller/torrents/action/#{command}/#{hash}"

  update = ->
    jq.get "/homecontroller/torrents/list", (data) ->
      processData data


  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval

  startInterval = ->
    stopInterval()
    update()
    update_interval = startInterval ->
      update()
    , SLOW_UPDATE

  ws_generic.register "torrent-list", processData
  ge_refresh.register "torrent-list", update

  @update = update
  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

jq =>
  @torrents = new Torrents()
  jq(".main-button-box .linux-downloads").on "click", ->
    torrents.update()
    content_switch.switchContent "#linux-downloads-modal"

  jq("#linux-downloads-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
