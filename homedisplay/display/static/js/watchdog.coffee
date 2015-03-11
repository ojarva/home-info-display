jq ->
  setInterval ->
    parent.postMessage (+ new Date()), "*"
  , 2000
