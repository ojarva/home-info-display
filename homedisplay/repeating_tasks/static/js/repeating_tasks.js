var RepeatingTasks = function(elem, use_date) {
  var parent_elem = $(elem), this_date = use_date, update_interval;

  function clearTasks() {
    $(parent_elem).children().remove();
  }

  function onReceiveItemWS(message) {
    processData(message);
  }

  function processData(data) {
    clearTasks();
    $.each(data, function() {
      var overdue_by = "", diff;
      if (this.fields.last_completed_at) {
        diff = moment(this.fields.last_completed_at).add(this.fields.repeat_every_n_seconds, "seconds");
        overdue_by = " (<span class='auto-fromnow-update' data-timestamp='" + diff + "'>" + diff.fromNow() + "</span>)";
      }
      if (this.fields.optional) {
        icon = "fa-question-circle";
      } else {
        icon = "fa-repeat";
      }
      parent_elem.append("<li class='repeating-task-mark-done' data-id='" + this.pk + "'><i class='fa-li fa " + icon + "'></i> <span class='task-title'>" + this.fields.title + "</span>" + overdue_by + "</li>");
    });
    parent_elem.find(".repeating-task-mark-done").on("click", function() {
      content_switch.userAction();
      var this_elem = $(this);
      var id = this_elem.data("id");
      $("#confirm-repeating-task").data("id", id);
      $("#confirm-repeating-task .task-title").html(this_elem.find(".task-title").html());
      content_switch.switchContent("#confirm-repeating-task");
    });
  }

  function update() {
    $.get("/homecontroller/repeating_tasks/get_json/" + this_date, function(data) {
      processData(data);
    });
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, 1000 * 60 * 120);
    ws_generic.register("repeating_tasks_" + this_date, onReceiveItemWS);
    ge_refresh.register("repeating_tasks_" + this_date, update);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    ws_generic.deRegister("repeating_tasks_" + this_date);
    ge_refresh.deRegister("repeating_tasks_" + this_date);
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
  this.update = update;
  this.clearTasks = clearTasks;
};

var tasks_today, tasks_tomorrow, tasks_all;

$(document).ready(function() {
  tasks_today = new RepeatingTasks("#today .list-repeating-tasks .fa-ul", "today");
  tasks_tomorrow = new RepeatingTasks("#tomorrow .list-repeating-tasks .fa-ul", "tomorrow");
  tasks_all = new RepeatingTasks("#repeating-tasks-all .fa-ul", "all");
  tasks_today.startInterval();
  tasks_tomorrow.startInterval();
  tasks_all.startInterval();
  $("#confirm-repeating-task .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
  $("#confirm-repeating-task .yes").on("click", function () {
    var id = $("#confirm-repeating-task").data("id");
    $.get("/homecontroller/repeating_tasks/done/" + id, function() {
    });
    content_switch.switchContent("#main-content");
  });
  $("#confirm-repeating-task .snooze").on("click", function () {
    var id = $("#confirm-repeating-task").data("id");
    $.get("/homecontroller/repeating_tasks/snooze/" + id + "/" + $(this).data("days"), function() {
    });
    content_switch.switchContent("#main-content");
  });

  $("#confirm-repeating-task .cancel").on("click", function () {
    content_switch.switchContent("#main-content");
  });

  $(".main-button-box .repeating").on("click", function() {
    content_switch.switchContent("#repeating-tasks-all");
  });

  $("#repeating-tasks-all .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });

});
