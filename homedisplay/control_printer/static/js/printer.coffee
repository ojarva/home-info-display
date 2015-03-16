Printer = ->

  update_interval = null
  clearLabels = ->
    jq(".printer-labels").children().remove()

  removeCheck = ->
    #TODO: only remove relevant check mark(s).
    jq(".printer-labels i").removeClass("fa-check")


  printLabel = (id) ->
    jq.post "/homecontroller/printer/print_label",
      "id": id
    , (data) ->
      jq ".printer-labels .print-label-#{id} i"
      .removeClass "fa-spin fa-spinner"
      .addClass "fa-check"
      setTimeout removeCheck, 2000


  processLabels = (data) ->
    clearLabels()
    main_elem = jq ".printer-labels"
    jq.each data, ->
      main_elem.append "<div class='center-content stripe-box animate-click action-button print-label-#{@pk}' data-id='#{@pk}'>#{@fields.name} <i class='fa fa-fw'></i></div>"

    #TODO: Bind click events
    main_elem.find("div").on "click", ->
      content_switch.userActivity()
      jq(@).find("i").addClass "fa-spin fa-spinner"
      printLabel jq(@).data "id"

  updateLabels = ->
    jq.get "/homecontroller/printer/get_labels", (data) ->
      processLabels data

  fetchStatus = ->
    main = jq "#print-modal .printer-jobs-content"
    main.find("li").remove()
    main.slideUp()
    jq("#print-modal .printer-jobs .spinner").slideDown()
    jq.get "/homecontroller/printer/get_status", (data) ->
      jq("#print-modal .printer-jobs .spinner").slideUp()
      main.slideDown()
      jq.each data, (key, value) ->
        creationTime = moment(value["time-at-creation"]).fromNowSynced()
        main.find("ul").append "<li data-id='#{key}'><i class='fa-li fa fa-times-circle'></i>Luotu #{creationTime}</i>"

      main.find("li").on "click", ->
        content_switch.userActivity()
        id = jq(@).data "id"
        jq.post "/homecontroller/printer/cancel_job/#{id}", ->
          fetchStatus()

  fetchPrinters = ->
    status_main = jq "#print-modal .printer-status"
    status_main.find(".printer-status-content").hide().children().remove()
    status_main.find(".spinner").slideDown()
    jq.get "/homecontroller/printer/get_printers", (data) ->
      status_main.find(".spinner").slideUp()
      status_main.find(".printer-status-content").slideDown()
      jq.each data, (key, value) ->
        state = value["printer-state"]
        states =
          3: "odottaa"
          4: "tulostaa"
          5: "pysäytetty"
        status_main.find(".printer-status-content").append "<h2>#{key} (#{states[state]})</h2><p>Status: #{value["printer-state-message"]}</p>"

   startInterval = ->
    stopInterval()
    updateLabels()
    update_interval = setInterval updateLabels, SLOW_UPDATE


   stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval

  ge_refresh.register "printer-labels", updateLabels
  ws_generic.register "printer-labels", processLabels


  @fetchStatus = fetchStatus
  @fetchPrinters = fetchPrinters
  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

jq =>
  obj = @
  obj.printer = new Printer()
  obj.printer.startInterval()

  jq(".main-button-box .print-labels").on "click", ->
    content_switch.switchContent "#print-modal"
    obj.printer.fetchStatus()
    obj.printer.fetchPrinters()

  jq("#print-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
