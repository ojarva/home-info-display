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

  processData = (data) ->
    resetWeatherInfo()

    if data.main_forecasts.suninfo?
      suninfo = data.main_forecasts.suninfo
      for own key, value of suninfo
        sunrise = moment value.sunrise, "YYYYMMDDTHHmmss"
        sunset = moment value.sunset, "YYYYMMDDTHHmmss"

        weather.find(".sunrise").html """<span class="fa-stack fa-lg"><i class="fa fa-sun-o fa-stack-1x"></i><i class="fa fa-angle-up fa-stack-1x"></i></span> #{sunrise.format("HH:mm")}        (<span class="auto-fromnow-update" data-timestamp="#{sunrise}">#{sunrise.fromNowSynced()}</span>)"""
        weather.find(".sunset").html """<span class="fa-stack fa-lg"><i class="fa fa-sun-o fa-stack-1x"></i><i class="fa fa-angle-down fa-stack-1x"></i></span> #{sunset.format("HH:mm")} (<span class="auto-fromnow-update" data-timestamp="#{sunset}">#{sunset.fromNowSynced()}</span>)"""

    current_index = 1
    first_date = false
    new_day = false

    if data.main_forecasts? and data.main_forecasts.observations?
      for own key, value of data.main_forecasts.observations
        d = value[0]
        weather.find(".temperature-now").html """<span class="value">#{d.Temperature}&deg;C</span>"""
        weather.find(".wind-now").html """<span class="value">#{d.WindSpeedMS} - #{d.WindGust}m/s</span>"""
        direction = d.WindCompass8
        weather.find(".wind-direction-now").html "<i class='fa fa-fw fa-long-arrow-up fa-rotate-#{direction}'></i>"

        weather.find(".humidity-now").html """<span class="type">Ilmankosteus: </span><span class="value">#{d.Humidity}%</span>"""
        weather.find(".real-temperature-now").html """<span class="type">Lämpötila: </span><span class="value">#{d.Temperature}&deg;C</span>"""
        weather.find(".dewpoint-now").html """<span class="type">Kastepiste: </span><span class="value">#{d.DewPoint}&deg;C</span>"""
        weather.find(".rainfall-now").html """<span class="type">Sade: </span><span class="value">#{d.RI_10MIN}mm</span>"""
        weather.find(".visibility-now").html """<span class="type">Näkyvyys: </span><span class="value">#{Math.round(d.Visibility/1000)}km</span>"""
        weather.find(".cloudiness-now").html """<span class="type">Pilvisyys: </span><span class="value">#{d.TotalCouldCover}/8</span>"""

        a = d.WW_AWS
        stat = getAWS parseInt(a)
        weather.find(".description-now").html """<span class="value">#{stat}</span>"""


    if data? and data.marine_observations?
      d = data.marine_observations
      marine = weather.find ".marine-now"
      marine.find(".marine-wind-now").html """<span class="type">Tuuli: </span><span class="value">#{d.wind_speed.value} - #{d.wind_gust.value}m/s</span>"""

    current_index = 13
    now = clock.getMoment()
    current_row = null
    highlight_set = false
    last_header = null
    new_item = """<div class="col-md-1">
      <span class="timestamp"><i class="fa fa-question-circle"></i></span><br>
      <span class="symbol"><i class="fa fa-question-circle"></i></span><br>
      <span class="temperature"><i class="fa fa-question-circle"></i></span>
      <span class="wind-direction"></span><span> </span>
      <span class="wind-speed"><i class="fa fa-question-circle"></i></span><span class="wind-speed-unit">m/s</span>
    </div>"""
    current_day = null
    days = 0

    if data.main_warnings?
      w = data.main_warnings.warnings
      warnings = weather.find ".weather-warnings"

      sea = w.sea.replace new RegExp("<br/>", "g"), ""
      console.log sea
      warnings.html """<span class="weather-warning"><i class="fa fa-female"></i> #{w.pedestrian}</span>
                       <span class="weather-warning"><i class="fa fa-ship"></i> #{sea}</span>
                       <span class="weather-warning"><i class="fa fa-car"></i> #{w.road}</span>
                       <span class="weather-warning"><i class="fa fa-pagelines"></i> #{w.land}</span>
                       """

    jq.each data.main_forecasts.forecasts[0].forecast, ->
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

      current_row.append new_item
      current_item = current_row.find(".col-md-1").last()

      current_item.find(".timestamp").html "#{timestamp.hour()}:00"
      current_item.find(".temperature").html "#{@FeelsLike}&deg;C"
      current_item.find(".symbol").html """<img src="/homecontroller/static/byo-images/#{@WeatherSymbol3}.png">"""
      current_item.find(".temperature-unit").html "&deg;C"
      current_item.find(".wind-speed").html Math.round(@WindSpeedMS)
      if @WindDirection?
        direction = @WindCompass8
        current_item.find(".wind-direction").html "<i class='fa fa-fw fa-long-arrow-up fa-rotate-#{direction}'></i>"

      current_index += 1

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
