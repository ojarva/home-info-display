Notifications = (elem) ->
  jq_elem = jq elem
  jq_elem.empty()

  updateItems = (item_type, desc_string, can_dismiss) ->
    updated = false
    jq.each jq_elem.children(), ->
      if jq(@).data("item-type") == item_type
        # Matching element -> update
        jq(@).find(".content").html desc_string
        jq(@).data "can_dismiss", can_dismiss
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
        item_id = @pk

        if can_dismiss
          desc_string = """<i class="fa fa-times-circle-o"></i>
        #{description}"""
        else
          desc_string = """<i class="fa fa-info-circle"></i>
                #{description}"""


        updated = updateItems(item_type, desc_string, can_dismiss)

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

    return

  dismiss = (item_id) ->
    jq.delete "/notifications/dismiss/" + item_id

  update = ->
    jq.get "/notifications/status", (data) ->
      processData data

  update()
  ws_generic.register "notifications", processData
  ge_refresh.register "notifications", update

  jq(document).on "click", ".notification-item", ->
    if !jq(@).data("can-dismiss") == true
      return
    dismiss jq(@).data("item-id")

  return @

jq =>
  @notifications = new Notifications("#notifications")
