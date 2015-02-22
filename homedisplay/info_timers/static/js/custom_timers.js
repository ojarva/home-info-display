var CustomTimer = function(options) {
  options = options || {};
  var duration_elem = $(options.duration_elem);
  var modal_elem = $(options.modal_elem);
  var time_spec = {"h_s": 0, "h_l": 3, "m_s": 3, "m_l": 2, "s_s": 5, "s_l": 2};

  function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
  }

  function getTimeField(content, field) {
    var d = content.substring(time_spec[field + "_s"], time_spec[field + "_s"] + time_spec[field + "_l"]);
    return d;

  }
  function setTimeField(content, field, data) {
    var index_start = time_spec[field + "_s"];
    var length = time_spec[field + "_l"];
    var d = content.substring(0, index_start) + data + content.substring(index_start + length);
    return d;
  }

  function nullTimeField(content, field) {
    var replace_string = "";
    for (var i = 0; i < time_spec[field + "_l"]; i++) {
      replace_string += "0";
    }
    return setTimeField(content, field, replace_string);
  }

  function processButton(content) {
    var current_content = duration_elem.data("content");
    if (content.substring(0, 6) == "clear-") {
      // backspace
      var clear_field = content.substring(6);
      current_content = nullTimeField(current_content, clear_field);
    } else {
      var data = parseInt(content.substring(0, content.length - 1));
      var field = content.substring(content.length - 1);
      var field_data = parseInt(getTimeField(current_content, field));
      field_data += data;
      if (field_data < 0) {
        var hours_field = parseInt(getTimeField(current_content, "h"));
        var minutes_field = parseInt(getTimeField(current_content, "m"));
        if (field == "s") {
          if (minutes_field == 0 && hours_field > 0) {
            // Take 1h to minutes field.
            hours_field -= 1;
            current_content = setTimeField(current_content, "h", zeroPad(hours_field, time_spec.h_l));
            minutes_field += 60;
          }
          if (minutes_field > 0) {
            // Take 1 minute to seconds field.
            minutes_field -= 1;
            field_data += 60;
            current_content = setTimeField(current_content, "m", zeroPad(minutes_field, time_spec.m_l));
          } else {
            field_data = 0;
          }
        } else if (field == "m") {
          if (hours_field > 0) {
            // Take 1 hour to minutes field.
            hours_field -= 1;
            field_data += 60;
            current_content = setTimeField(current_content, "h", zeroPad(hours_field, time_spec.h_l));
          } else {
            field_data = 0;
          }
        } else {
          field_data = 0;
        }
      }
      if ((field == "s" || field == "m") && field_data >= 60) {
        if (field == "s") {
          minutes_field = parseInt(getTimeField(current_content, "m"));
          minutes_field += 1;
          field_data -= 60;
          if (minutes_field >= 60) {
            minutes_field -= 60;
            hours_field = parseInt(getTimeField(current_content, "h"));
            hours_field += 1;
            current_content = setTimeField(current_content, "h", zeroPad(hours_field, time_spec.h_l));
          }
          current_content = setTimeField(current_content, "m", zeroPad(minutes_field, time_spec.m_l));
        }
        if (field == "m") {
          field_data -= 60;
          hours_field = parseInt(getTimeField(current_content, "h"));
          hours_field += 1;
          current_content = setTimeField(current_content, "h", zeroPad(hours_field, time_spec.h_l));
        }
      }
      field_data = zeroPad(field_data, time_spec[field + "_l"]);
      current_content = setTimeField(current_content, field, field_data);
    }
    duration_elem.data("content", current_content);
    var c = current_content;
    duration_elem.html(c.substr(0, 3) + ":" + c.substr(3, 2) + ":" + c.substr(5, 2));
  }

  function submitTimer(name) {
    var c = duration_elem.data("content");
    var seconds = parseInt(c.substr(0, 3)) * 3600 + parseInt(c.substr(3, 2)) * 60 + parseInt(c.substr(5, 2));
    if (seconds == 0) {
      seconds = $(this).data("duration");
    }
    if (typeof seconds == "undefined") {
    } else {
      var timer_run = new Timer("#timer-holder", {"name": name, "duration": seconds});
    }
    modal_elem.find(".close").click();
  }

  function closeCustomTimer() {
    var c = "0000000";
    duration_elem.data("content", c);
    duration_elem.html(c.substr(0, 3) + ":" + c.substr(3, 2) + ":" + c.substr(5, 2));

    switchVisibleContent("#main-content");
  }

  function showCustomTimer() {
    switchVisibleContent("#add-custom-timer");
  }

  this.showCustomTimer = showCustomTimer;
  this.closeCustomTimer = closeCustomTimer;
  this.submitTimer = submitTimer;
  this.processButton = processButton;
  this.setTimeField = setTimeField;
  this.getTimeField = getTimeField;
  this.nullTimeField = nullTimeField;

  modal_elem.find(".add-timer-button").on("click", function () {
    var content = $(this).data("content").trim();
    processButton(content);
  });

  modal_elem.find(".timer-description-button").on("click", function() {
    var name = $(this).html();
    submitTimer(name);
  });

  $(".add-custom-timer-plus").on("click", function() {
    showCustomTimer();
  });

  modal_elem.find(".close").on("click", function () {
    closeCustomTimer();
  });
};

var custom_timer;

$(document).ready(function () {
  custom_timer = new CustomTimer({duration_elem: "#custom-timer-duration", modal_elem: "#add-custom-timer"});
});
