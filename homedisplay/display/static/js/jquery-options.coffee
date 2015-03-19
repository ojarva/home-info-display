@jq = jQuery.noConflict()

# Adapted from http://stackoverflow.com/a/22786755/592174
jQuery.each ["put", "delete", "patch"], (i, method) ->
  jQuery[method ] = (url, data, callback, type) ->

    if jQuery.isFunction data
      type = type or callback
      callback = data
      data = undefined

    return jQuery.ajax
      url: url
      type: method
      dataType: type
      data: data
      success: callback
