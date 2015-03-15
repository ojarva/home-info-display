jq ->
  height = jq(window).height()
  jq(".content-box").css
    "height": height
  .css
    "min-height": height
