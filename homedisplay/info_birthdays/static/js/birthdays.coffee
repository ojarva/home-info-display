Birthdays = (elem, use_date, options) ->
  options = options || {}
  options.showdate = options.showdate || false
  options.maxitems = options.maxitems || 100000
  this_date = use_date
  update_interval = null
  current_item = 0
  items_in_current = 0
  parent_elem = jq(elem).slice 0, 1

  onReceiveItemWS = (message) ->
    processData message


  clearDates = ->
    jq(elem).find("li").remove()
    items_in_current = 0
    current_item = 0
    parent_elem = jq(elem).slice(current_item, 1)


  compareBirthdays = (a, b) ->
    if a.birthday_sort < b.birthday_sort
      return -1

    if a.birthday_sort > b.birthday_sort
      return 1
    return 0


  formatSortString = (da) ->
    da = moment da
    m = da.month()
    if m < 10
      m = "0#{m}"

    d = da.date()
    if d < 10
      d = "0#{d}"

    return "#{m}#{d}"


  processData = (data) ->
    debug.log("Processing #{data.length} birthdays for #{this_date}")
    clearDates()
    data_sortable = []
    now = clock.getMoment().subtract 1, "days"
    now_str = formatSortString now

    # Add sortable field
    jq.each data, ->
      a = moment @fields.birthday
      sort_string = formatSortString a
      @birthday_moment = a
      prefix = "0"
      @next_year = false
      if sort_string < now_str
        prefix = "1"
        @next_year = true

      @birthday_sort = prefix + sort_string
      data_sortable.push this

    # Sort
    data_sortable.sort compareBirthdays

    # Loop over sorted entries
    jq.each data_sortable, ->
      name = @fields.name
      age = ""
      date = ""
      extra = ""
      if @fields.nickname
        name = @fields.nickname

      if @fields.valid_year
        b = moment @birthday_moment
        b = b.year now.year()
        if @next_year
          b = b.add 1, "year"

        age = (" (" + @birthday_moment.from(b) + ")").replace(" sitten", "")

      if options.showdate
        date = " - " + @birthday_moment.date() + "." + (@birthday_moment.month() + 1) + "."
        if @fields.valid_year
          date += @birthday_moment.year()

      if items_in_current > options.maxitems
        current_item += 1
        if current_item > 3
          return false

        parent_elem = jq(elem).slice(current_item, current_item + 1)
        items_in_current = 0

      items_in_current += 1
      if this_date == "tomorrow"
        extra = " (huomenna)"

      parent_elem.append "<li><i class='fa-li fa fa-birthday-cake'></i> #{name}#{date}#{age}#{extra}</li>"

  update = ->
    jq.get "/homecontroller/birthdays/get_json/#{this_date}", (data) ->
      processData data


  startInterval = ->
    update()
    ws_generic.register "birthdays_#{this_date}", onReceiveItemWS
    ge_refresh.register "birthdays_#{this_date}", update
    ge_intervals.register "birthdays_#{this_date}", "daily", update

  stopInterval = ->
    ws_generic.deRegister "birthdays_#{this_date}"
    ge_refresh.deRegister "birthdays_#{this_date}"
    ge_intervals.deRegister "birthdays_#{this_date}", "daily"


  @startInterval = startInterval
  @stopInterval = stopInterval
  return this

jq =>
  this.birthdays_today = new Birthdays "#today .list-birthdays .fa-ul", "today"
  this.birthdays_tomorrow = new Birthdays "#tomorrow .list-birthdays .fa-ul", "tomorrow"
  this.birthdays_all = new Birthdays "#birthdays-list-all .fa-ul", "all",
    interval: 60 * 60 * 1000
    showdate: true
    maxitems: 45

  this.birthdays_today.startInterval()
  this.birthdays_tomorrow.startInterval()
  this.birthdays_all.startInterval()

  jq(".main-button-box .birthdays").on "click", ->
    content_switch.switchContent "#birthdays-list-all"

  jq("#birthdays-list-all .close").on "click",->
    content_switch.switchContent "#main-content"
