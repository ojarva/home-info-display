function refreshCallback() {
  setTimeout(function() {
    $(".navbar .refresh").removeClass("fa-spin");
  }, 1500);
}

$(document).ready(function() {
  ge_refresh.setRefreshCallback(refreshCallback);
  $(".navbar-brand").on("click", function() {
    content_switch.switchContent("#main-content");
  });
  $(".navbar .refresh").on("click", function () {
    $(this).addClass("fa-spin");
    ge_refresh.requestUpdate();
  });
});
