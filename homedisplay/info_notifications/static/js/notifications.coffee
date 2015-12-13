Notifications = (elem) ->
  jq_elem = jq elem
  jq_elem.empty()


  formatString = (fmt, elapsed_since, from_now_timestamp) ->
    if elapsed_since?
      fmt = fmt.replace(new RegExp("\\{elapsed_since\\}", "gm"), "<span class='auto-timer-update' data-timestamp='#{elapsed_since}'></span>")
    if from_now_timestamp?
      fmt = fmt.replace(new RegExp("\\{from_now_timestamp\\}", "gm"), "<span class='auto-fromnow-update' data-timestamp='#{from_now_timestamp}'></span>")
    return fmt

  updateItems = (item_type, desc_string, can_dismiss, elapsed_since, from_now_timestamp) ->
    updated = false
    jq.each jq_elem.children(), ->
      if jq(@).data("item-type") == item_type
        # Matching element -> update
        jq(@).find(".content").html(formatString(desc_string, elapsed_since, from_now_timestamp))
        jq(@).data "can-dismiss", can_dismiss
        jq(@).data "updated", "true"
        updated = true
        return updated
    return updated

  processData = (data) ->
    if data?
      items = []
      jq.each data, ->
        item_type = @fields.item_type
        description = @fields.description
        timestamp = @fields.timestamp
        can_dismiss = @fields.can_dismiss
        from_now_timestamp = @fields.from_now_timestamp
        elapsed_since = @fields.elapsed_since
        item_id = @pk

        if can_dismiss
          desc_string = formatString("""<i class="fa fa-times-circle-o"></i>
        #{description}""", elapsed_since, from_now_timestamp)
        else
          desc_string = formatString("""<i class="fa fa-info-circle"></i>
                #{description}""", elapsed_since, from_now_timestamp)


        updated = updateItems(item_type, desc_string, can_dismiss, elapsed_since, from_now_timestamp)

        if !updated
          # No matching element found -> create a new one
          jq_elem.append """<div class="notification-item notification-striping notification-item-#{item_type}" data-updated="true" data-item-type="#{item_type}" data-can-dismiss="#{can_dismiss}" data-item-id="#{item_id}">
            <div class="notification-container">
              <div class="content">
                #{desc_string}
              </div>
            </div>
          </div>"""
        items.push item_id

      jq.each jq_elem.children(), ->
        a = jq @
        if a.data("item-id") not in items
          a.remove()

      moment_auto_update.update()
      timer_auto_update.update()

    return

  dismiss = (item_id) ->
    jq.delete "/notifications/dismiss/" + item_id, ->
      update()

  update = ->
    jq.get "/notifications/status", (data) ->
      processData data

  update()
  ws_generic.register "notifications", processData
  ge_refresh.register "notifications", update

  jq(document).on "click", ".notification-item", ->
    if jq(@).data("can-dismiss") != true
      return
    dismiss jq(@).data("item-id")

  return @

jq =>
  @notifications = new Notifications("#notifications")
