RepeatingTasks = (elem, use_date) ->

  parent_elem = jq elem
  update_interval = null


  clearTasks = ->
    jq(parent_elem).children().remove()


  processData = (data) ->
    clearTasks()
    jq.each data, ->
      overdue_by = ""
      if @fields.last_completed_at
        diff = moment(@fields.last_completed_at).add @fields.repeat_every_n_seconds, "seconds"
        overdue_by = " (<span class='auto-fromnow-update' data-timestamp='#{diff}'>" + diff.fromNowSynced() + "</span>)"

      if @fields.optional
        icon = "fa-question-circle"
      else
        icon = "fa-repeat"

      added_elem = parent_elem.append """<li class='repeating-task-mark-done' data-id='#{@pk}' data-snooze-to-show='#{@fields.snooze_to_show}'>
        <i class='fa-li fa #{icon}'></i>
        <span class='task-title'>#{@fields.title}</span>#{overdue_by}
      </li>"""
      added_elem.find("li").data
        "history": JSON.stringify(@fields.history)

    parent_elem.find(".repeating-task-mark-done").on "click", ->
      content_switch.userActivity()
      repeating_task = jq @
      id = repeating_task.data "id"
      jq("#confirm-repeating-task").data "id", id
      jq("#confirm-repeating-task .task-title").html repeating_task.find(".task-title").html()

      snooze_to_show = repeating_task.data "snooze-to-show"
      snooze_immediately = jq "#confirm-repeating-task .snooze-immediately"
      if snooze_to_show < 0
        snooze_immediately.show()
        snooze_immediately.data "days", snooze_to_show
      else
        snooze_immediately.hide()


      task_history = jq "#confirm-repeating-task .task-history ul"
      task_history.children().remove()
      tasks = JSON.parse repeating_task.data("history")
      jq.each tasks, ->
        parsed = moment @fields.completed_at
        task_history.append "<li>" + parsed.format("YYYY-MM-DD") + " (" + parsed.fromNowSynced() + ")</li>"

      content_switch.switchContent "#confirm-repeating-task"

  onReceiveItemWS = (message) ->
    processData message

  update = ->
    jq.get "/homecontroller/repeating_tasks/get_json/#{use_date}", (data) ->
      processData data

  stopInterval = ->
    ws_generic.deRegister "repeating_tasks_#{use_date}"
    ge_refresh.deRegister "repeating_tasks_#{use_date}"
    ge_intervals.deRegister "repeating_tasks_#{use_date}", "daily"
    return

  startInterval = ->
    stopInterval()
    update()
    ws_generic.register "repeating_tasks_#{use_date}", onReceiveItemWS
    ge_refresh.register "repeating_tasks_#{use_date}", update
    ge_intervals.register "repeating_tasks_#{use_date}", "daily", update
    return

  @startInterval = startInterval
  @stopInterval = stopInterval
  @update = update
  @clearTasks = clearTasks
  return @

jq =>
  @tasks_today = new RepeatingTasks "#today .list-repeating-tasks .fa-ul", "today"
  @tasks_tomorrow = new RepeatingTasks "#tomorrow .list-repeating-tasks .fa-ul", "tomorrow"
  @tasks_all = new RepeatingTasks "#repeating-tasks-all .fa-ul", "all"
  @tasks_today.startInterval()
  @tasks_tomorrow.startInterval()
  @tasks_all.startInterval()

  jq("#confirm-repeating-task .close").on "click", ->
    content_switch.switchContent "#main-content"

  jq("#confirm-repeating-task .yes").on "click", ->
    id = jq("#confirm-repeating-task").data "id"
    jq.post "/homecontroller/repeating_tasks/done/#{id}"
    content_switch.switchContent "#main-content"

  jq("#confirm-repeating-task .snooze").on "click", ->
    id = jq("#confirm-repeating-task").data "id"
    jq.post "/homecontroller/repeating_tasks/snooze/#{id}/" + jq(@).data("days")
    content_switch.switchContent "#main-content"

  jq("#confirm-repeating-task .cancel").on "click", ->
    content_switch.switchContent "#main-content"

  jq(".main-button-box .repeating").on "click", ->
    content_switch.switchContent "#repeating-tasks-all"

  jq("#repeating-tasks-all .close").on "click", ->
    content_switch.switchContent "#main-content"
