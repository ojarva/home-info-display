RefreshWeather = (options) ->
  options = options or {}
  options.elem = options.elem or "#weather-general"
  options.update_interval = options.update_interval or FAST_UPDATE

  elem = jq options.elem
  update_interval = null

  setWeatherInfo = (icon, temperature) ->
    elem.html "<img src='/homecontroller/static/images/#{icon}.png'><br> #{temperature}&deg;C"

  resetWeatherInfo = ->
    elem.html "<i class='fa fa-question-circle'></i>"

  update = ->
    jq.get "/homecontroller/weather/get_json?" + (new Date()).getTime(), (data) ->
      resetWeatherInfo()
      if data? and data.current?
        setWeatherInfo data.current.icon, data.current.feels_like

  startInterval = ->
    update()
    update_interval = setInterval ->
      update()
    , options.update_interval

  stopInterval = ->
    if update_interval?
      update_interval = clearInterval update_interval

  @update = update
  @startInterval = startInterval
  @stopInterval = stopInterval
  return @

jq =>
  @refresh_weather = new RefreshWeather
    "elem": "#weather-general"
  @refresh_weather.startInterval()
