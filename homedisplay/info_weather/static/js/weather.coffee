RefreshWeather = (options) ->
  options = options || {}
  weather = jq ".weather"

  resetWeatherInfo = ->
    weather.find(".weather-box span").html "<i class='fa fa-question-circle'></i>"
    weather.find(".data-field").html "<i class='fa fa-question-circle'></i>"
    weather.find(".weather-box").removeClass "new-day" # Remove "day changed" separator line
    jq(".weather-all").children().remove()

  processData = (data) ->
    resetWeatherInfo()
    debug.log("Processing weather data with " + data.hours.length + " items")
    if data.sun?
      sunrise = moment data.sun.sunrise
      sunset = moment data.sun.sunset
      jq(".sun-info").html("<i class='fa fa-sun-o'></i><i class='fa fa-long-arrow-up'></i> " + sunrise.format("HH:mm") + " (<span class='auto-fromnow-update' data-timestamp='" + sunrise + "'>" + sunrise.fromNowSynced() + "</span>) <i class='fa fa-sun-o'></i><i class='fa fa-long-arrow-down'></i> " + sunset.format("HH:mm") + " (<span class='auto-fromnow-update' data-timestamp='" + sunset + "'>" + sunset.fromNowSynced() + "</span>)")

    items = jq(".weather")
    current_index = 1
    first_date = false
    new_day = false
    if data? and data.current? and data.current.feels_like?
      weather.find(".temperature-now").html(data.current.feels_like)
      weather.find(".wind-now").html(data.current.wind_speed_readable)
      direction = (data.current.wind_direction_degrees + "").replace(".", "_")
      weather.find(".wind-direction-now").html("<i class='fa fa-fw fa-long-arrow-up fa-rotate-"+direction+"'></i>")

    jq.each data.next, ->
      this_item = weather.find(".weather-" + current_index)
      if first_date == false
        first_date = @item.date
      else if new_day == false
        if first_date != @item.date
          this_item.addClass "new-day"
          new_day = true

      this_item.find(".timestamp").html(@name)
      this_item.find(".temperature").html(@item.feels_like)
      this_item.find(".symbol").html("<img src='/homecontroller/static/images/" + @item.icon + ".png'>")
      this_item.find(".temperature-unit").html("&deg;C")
      current_index += 1

    current_index = 13

    now = clock.getMoment()
    current_row = null
    highlight_set = false
    last_header = null
    new_item = "<div class='col-md-1'><span class='timestamp'><i class='fa fa-question-circle'></i></span><br><span class='temperature'><i class='fa fa-question-circle'></i></span><span class='temperature-unit'>&deg;C</span><span class='symbol'><i class='fa fa-question-circle'></i></span><br><span class='wind-direction'></span><span> </span> <span class='wind-speed'><i class='fa fa-question-circle'></i></span><span class='wind-speed-unit'>m/s</span></div>";
    jq.each data.hours, ->
      if @hour % 2 != 0
        return true # continue

      if current_index > 11
        current_index = 0
        jq(".weather-all").append("<div class='row'><div class='col-md-12'><h2></h2></div></div><div class='row'></div>")
        current_row = jq(".weather-all .row").last()
        last_header = jq(".weather-all h2").last()
        last_header.html(@weekday_fi + " " + @date)

      current_row.append(new_item)
      current_item = current_row.find(".col-md-1").last()

      current_item.find(".timestamp").html(@hour + ":00")
      current_item.find(".temperature").html(@feels_like)
      current_item.find(".symbol").html("<img src='/homecontroller/static/images/" + @icon + ".png'>")
      current_item.find(".temperature-unit").html("&deg;C")
      current_item.find(".wind-speed").html(Math.round(@wind_speed / 3.6))
      if @wind_direction_degrees?
        direction = (@wind_direction_degrees + "").replace(".", "_")
        current_item.find(".wind-direction").html("<i class='fa fa-fw fa-long-arrow-up fa-rotate-"+direction+"'></i>")

      if !highlight_set and @date == now.format("YYYY-MM-DD") and (now.hour() == @hour or now.hour() - 1 == @hour)
        current_item.addClass("weather-today")
        highlight_set = true

      current_index += 1

  update = ->
    jq.get "/homecontroller/weather/get_json", (data) ->
      processData data

  onReceiveItemWS = (data) ->
    processData data

  startInterval = ->
    update()
    ws_generic.register("weather", onReceiveItemWS)
    ge_refresh.register("weather", update)
    ge_intervals.register("weather", "hourly", update)

  stopInterval = ->
    ws_generic.deRegister "weather"
    ge_refresh.deRegister "weather"
    ge_intervals.deRegister "weather", "hourly"

  @startInterval = startInterval
  @stopInterval = stopInterval
  return this


refresh_weather = null

jq ->

  refresh_weather = new RefreshWeather()
  refresh_weather.startInterval()
  jq(".open-weather-modal").on "click", ->
    content_switch.switchContent "#weather-modal"

  jq("#weather-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
