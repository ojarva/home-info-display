function refreshCallback() {
  setTimeout(function() {
    jq(".navbar .refresh").removeClass("fa-spin");
  }, 1500);
}

jq(document).ready(function() {
  ge_refresh.setRefreshCallback(refreshCallback);
  jq(".navbar-brand").on("click", function() {
    content_switch.switchContent("#main-content");
  });
  jq(".navbar .refresh").on("click", function () {
    jq(this).addClass("fa-spin");
    ge_refresh.requestUpdate();
  });
});
