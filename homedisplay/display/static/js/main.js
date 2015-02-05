function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function switchVisibleContent(elem) {
  $(".content-box").slideUp();
  $(elem).slideDown();
}

$(document).ready(function() {
  $(".animate-click").each(function () {
    $(this).data("original-bg-color", $(this).css("background-color"));
  })
  $(".animate-click").on("click", function () {
    $(this).stop(true).css("background-color", $(this).data("original-bg-color")).effect("highlight", {color: "#ffffff"}, 500);

  });
});
moment.locale("fi");
