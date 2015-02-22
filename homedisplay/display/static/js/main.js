moment.locale("fi");

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie("csrftoken");

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var switch_visible_content_timeout;
var switch_visible_content_currently_active;

function switchToMainContent() {
  $(switch_visible_content_currently_active).find(".close").trigger("click");
  if (switch_visible_content_timeout) {
    switch_visible_content_timeout = clearTimeout(switch_visible_content_timeout);
  }
}

function switchVisibleContent(elem) {
  if (switch_visible_content_timeout) {
    switch_visible_content_timeout = clearTimeout(switch_visible_content_timeout);
  }
  $(".content-box").slideUp(); // Hide all content boxes
  $("html, body").animate({ scrollTop: 0 }, "fast"); // Always scroll to top.
  $("#navbar").collapse("hide"); // Hide menu, if visible
  if (elem != "#main-content") {
    switch_visible_content_currently_active = elem;
    switch_visible_content_timeout = setTimeout(switchToMainContent, 60 * 1000);
    $(elem).slideDown();
  }
}

$(document).ready(function() {
  $(".animate-click").each(function () {
    $(this).data("original-bg-color", $(this).css("background-color"));
  });
  $(".animate-click").on("click", function () {
    $(this).stop(true).css("background-color", $(this).data("original-bg-color")).effect("highlight", {color: "#ffffff"}, 500);
  });

});
