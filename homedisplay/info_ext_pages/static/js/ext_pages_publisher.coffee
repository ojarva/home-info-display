jq ->
  jq("#open-ext-page").submit ->
    jq.post "/homecontroller/ext_pages/push/page",
      page: jq("#open-ext-page-url").val()
    , ->
      jq("#open-ext-page-url").val("")
    return false
