$(document).ready(function () {
  $(".add-timer-button").on("click", function () {
    var content = $(this).html().trim();
    var current_content = $("#custom-timer-duration").data("content");
    if (content.length > 2) {
      // backspace
      var d = current_content.substr(0, 6);
      current_content = "0"+d;
    } else {
      // Add to end
      if (current_content.substr(0, 1) == "0") {
        current_content += content;
        if (current_content.length > 7) {
          current_content = current_content.substr(current_content.length-7);
        }
      }
    }
    $("#custom-timer-duration").data("content", current_content);
    var c = current_content;
    $("#custom-timer-duration").html(c.substr(0,3)+":"+c.substr(3,2)+":"+c.substr(5,2));
  });

  $(".timer-description-button").on("click", function() {
    var name = $(this).html();
    var c = $("#custom-timer-duration").data("content");
    var seconds = parseInt(c.substr(0,3)) * 3600 + parseInt(c.substr(3,2)) * 60 + parseInt(c.substr(5,2));
    if (seconds == 0) {
      seconds = $(this).data("duration");
    }
    if (typeof seconds == "undefined") {
      console.log("No time available for custom timer");
    } else {
      var timer_run = new Timer("#timer-holder", {"name": name, "duration": seconds});
    }
    $("#close-add-custom-timer").click();
  });
  $("#submit-custom-timer").on("click", function () {
    var name = $(".timer-description-button-selected").html() || "Nimetön";
    var c = $("#custom-timer-duration").data("content");
    var seconds = parseInt(c.substr(0,3)) * 3600 + parseInt(c.substr(3,2)) * 60 + parseInt(c.substr(5,2));

    var timer_run = new Timer("#timer-holder", {"name": name, "duration": seconds});
    $("#close-add-custom-timer").click();
  });
  $("#add-custom-timer-plus").on("click", function() {
    $("#add-custom-timer").show();
    $("#main-content").hide();
  });
  $("#close-add-custom-timer").on("click", function () {
    $("#custom-timer-duration").data("content", "000000");
    var c = "0000000";
    $("#custom-timer-duration").html(c.substr(0,3)+":"+c.substr(3,2)+":"+c.substr(5,2));

    $("#add-custom-timer").hide();
    $("#main-content").show();
  });
});
