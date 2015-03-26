RefreshWeather = (options) ->
  options = options or {}
  weather = jq ".weather"

  fi_weekdays = ["ma", "ti", "ke", "to", "pe", "la", "su"]

  resetWeatherInfo = ->
    weather.find(".weather-box span").html "<i class='fa fa-question-circle'></i>"
    weather.find(".data-field").html "<i class='fa fa-question-circle'></i>"
    weather.find(".weather-box").removeClass "new-day" # Remove "day changed" separator line
    weather.find(".uv-warning").children().remove()
    weather.find(".now").find("span").children().remove()
    jq(".weather-all").children().remove()

  getAWS = (a) ->
    if a == 0 or (20 <= a <= 29)
      return "kirkasta"
    else if a == 4 or a == 5
      return "savua tai pölyä"
    else if a == 10
      return "usva"
    else if 30 <= a <= 34
      return "sumu"
    else if a == 40
      return "sadetta"
    else if 50 <= a <= 53
      return "tihkua"
    else if a == 60
      return "sadetta"
    else if a == 41
      return "kevyttä sadetta"
    else if a == 42
      return "rankkaa sadetta"
    else if 54 <= a <= 56
      return "jäätävää tihkua"
    else if a == 61
      return "kevyttä sadetta"
    else if a == 62
      return "sadetta" # moderate rain"
    else if a == 63
      return "rankkasadetta"
    else if a == 64
      return "kevyttä jäätävää tihkua"
    else if a == 65
      return "jäätävää sadetta"
    else if a == 66
      return "rankkaa jäätävää sadetta"
    else if a == 67
      return "kevyttä räntää"
    else if a == 68
      return "räntää"
    else if a == 70
      return "lunta"
    else if a == 71
      return "kevyttä lumisadetta"
    else if a == 72
      return "lumisadetta"
    else if a == 73
      return "rankkaa lumisadetta"
    else if 74 <= a <= 76
      return "rakeita"
    else if a == 80
      return "kuuroja"
    else if a == 81
      return "kevyitä kuuroja"
    else if a == 82
      return "kuuroja"
    else if a == 83 or a == 84
      return "rankkoja kuuroja"
    else if a == 85
      return "kevyitä lumikuuroja"
    else if a == 86
      return "lumikuuroja"
    else if a == 87
      return "rankkoja lumikuuroja"
    else
      return ""

  processWarnings = (data) ->
    warnings = weather.find ".weather-warnings"

    sea = data.warnings.sea.replace new RegExp("<br/>", "g"), ""
    warnings_html = ""
    warnings_early_html = ""
    warnings_data =
      "female": data.warnings.pedestrian
      "ship": sea
      "car": data.warnings.road
      "pagelines": data.warnings.land
    for own icon, warning of warnings_data
        if warning == "Ei varoituksia."
          continue
        else if warning == "Koko maassa vallitsee normaali ajokeli."
          continue
        else if warning == "Jalankulkukeli on tavanomainen koko maassa."
          continue
        warnings_html += """<span class="weather-warning"><i class="fa fa-#{icon}"></i> #{warning}</span> """

    early_warnings_data =
      "ship": data.early.sea,
      "car": data.early.road,
      "pagelines": data.warnings.land

    for own icon, warning of early_warnings_data
      if warning == "Ei varoituksia."
        continue
      warnings_early_html += """<span class="weather-warning"><i class="fa fa-#{icon}"></i> #{warning}</span> """

    if warnings_early_html.length > 0
      warnings_early_html = """<span class="weather-warning-type">Ennakkovaroitukset:</span> #{warnings_early_html}"""

    weather.find(".weather-warnings").html warnings_html
    weather.find(".weather-early-warnings").html warnings_early_html

  processSunInfo = (data) ->
    for own key, value of data
      sunrise = moment value.sunrise, "YYYYMMDDTHHmmss"
      sunset = moment value.sunset, "YYYYMMDDTHHmmss"
      weather.find(".suninfo").html """<span class="value">#{sunrise.format("HH:mm")}-#{sunset.format("HH:mm")}</span>"""

  setObservations = (elem, observations) ->
    for own key, value of observations
      d = value[0]
      elem.find(".temperature-now").html """<span class="value">#{d.Temperature}&deg;C</span>"""
      elem.find(".wind-now").html """<span class="value">#{Math.round(d.WindSpeedMS)}-#{Math.round(d.WindGust)}m/s</span>"""
      elem.find(".wind-direction-now").html "<i class='fa fa-fw fa-long-arrow-up fa-rotate-#{d.WindCompass8}'></i>"
      elem.find(".humidity-now").html """<span class="value">#{Math.round(d.Humidity)}%</span>"""
      elem.find(".real-temperature-now").html """<span class="value">#{d.Temperature}&deg;C</span>"""
      elem.find(".dewpoint-now").html """<span class="value">#{d.DewPoint}&deg;C</span>"""
      elem.find(".rainfall-now").html """<span class="value">#{d.RI_10MIN}mm</span>"""
      elem.find(".visibility-now").html """<span class="value">#{Math.round(d.Visibility/1000)}km</span>"""
      elem.find(".cloudiness-now").html """<span class="value">#{d.TotalCouldCover}/8</span>"""

      stat = getAWS parseInt(d.WW_AWS)
      elem.find(".description-now").html """<span class="value">#{stat}</span>"""

  processMarine = (data) ->
    marine = jq ".marine-weather"
    setObservations marine, data.observations

  processForecasts = (data) ->
    current_index = 13
    now = clock.getMoment()
    current_row = null
    highlight_set = false
    last_header = null
    current_day = null
    days = 0

    jq.each data, ->
      timestamp = moment @localtime, "YYYYMMDDTHHmmss"
      if timestamp.hour() % 2 != 0
        return true # Only add even hours

      weekday = fi_weekdays[timestamp.weekday()]
      date = timestamp.format "D.M."

      if current_index > 11 or (current_day? and current_day != date)
        if days >= 2
          return false # Show only current and next days
        current_index = 0
        jq(".weather-all").append """<div class="row">
          <div class="col-md-12">
            <h2></h2>
          </div>
        </div>
        <div class="row"></div>"""
        current_row = jq(".weather-all .row").last()
        last_header = jq(".weather-all h2").last()
        last_header.html "#{weekday} #{date}"
        current_day = date
        days += 1

      if @WindCompass8?
        # Do not show wind direction if no data is available - fallback is arrow pointing to north, which is
        # worse than showing nothing.
        wind_direction = "<i class='fa fa-fw fa-long-arrow-up fa-rotate-#{@WindCompass8}'></i>"
      else
        wind_direction = "<i class='fa fa-question-circle'></i>"

      current_row.append """<div class="col-md-1">
        <span class="timestamp">#{timestamp.format("HH")}:00</span><br>
        <span class="symbol"><img src="/homecontroller/static/byo-images/#{@WeatherSymbol3}.png"></span><br>
        <span class="temperature">#{@FeelsLike}&deg;C</span>
        <span class="wind-direction">#{wind_direction}</span><span> </span>
        <span class="wind-speed">#{Math.round(@WindSpeedMS)}</span><span class="wind-speed-unit">m/s</span>
      </div>"""

      current_index += 1

  processData = (data) ->
    resetWeatherInfo()

    if not data?
      console.warn "Received invalid data ", data
      return

    if data.main_forecasts?
      mf = data.main_forecasts
      if mf.suninfo?
        processSunInfo mf.suninfo

      if mf.observations?
        setObservations weather, mf.observations

      if mf.forecasts?
        processForecasts mf.forecasts[0].forecast

    if data.main_warnings?
      processWarnings data.main_warnings


    if data.marine_forecasts?
      processMarine data.marine_forecasts




  update = ->
    jq.get "/homecontroller/weather/get_json", (data) ->
      processData data

  onReceiveItemWS = (data) ->
    processData data

  startInterval = ->
    update()
    ws_generic.register "weather", onReceiveItemWS
    ge_refresh.register "weather", update
    ge_intervals.register "weather", "hourly", update

  stopInterval = ->
    ws_generic.deRegister "weather"
    ge_refresh.deRegister "weather"
    ge_intervals.deRegister "weather", "hourly"

  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

jq =>
  @refresh_weather = new RefreshWeather()
  @refresh_weather.startInterval()
  jq(".open-weather-modal").on "click", ->
    content_switch.switchContent "#weather-modal"

  jq("#weather-modal .close").on "click", ->
    content_switch.switchContent "#main-content"
