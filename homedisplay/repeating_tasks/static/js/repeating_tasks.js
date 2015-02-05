var RepeatingTasks = function(elem, use_date) {
  var parent_elem = $(elem), this_date = use_date, update_interval, wait_sync, ws4redis;

  function clearTasks() {
    $(parent_elem).children().remove();
  }

  function onReceiveItemWS(message) {
    if (message == "updated") {
      console.log("repeating tasks: backend requests update");
      update();
    }
  }

  function update() {
    $.get("/homecontroller/repeating_tasks/get_json/"+this_date, function(data) {
      clearTasks();
      $.each(data, function() {
        var overdue_by = "", diff;
        if (this.fields.last_completed_at) {
          diff = moment(this.fields.last_completed_at).add(this.fields.repeat_every_n_seconds, "seconds");
          overdue_by = " ("+diff.fromNow()+")";
        }
        parent_elem.append("<li class='repeating-task-mark-done' data-id='"+this.pk+"'><i class='fa-li fa fa-times-circle'></i> <span class='task-title'>"+this.fields.title+"</span>"+overdue_by+"</li>");
      });
      parent_elem.find(".repeating-task-mark-done").on("click", function() {
        var this_elem = $(this);
        var id = this_elem.data("id");
        $("#confirm-repeating-task").data("id", id);
        $("#confirm-repeating-task .task-title").html(this_elem.find(".task-title").html());
        switchVisibleContent("#confirm-repeating-task");
      });

    });
  }

  function runInterval() {
    update_interval = setInterval(update, 1800000); // 30min
  }

  function startInterval() {
    stopInterval();
    update();
    var now = new Date(), minutes, wait_time;
    minutes = now.getMinutes();
    // Sync intervals to run at 00:00:30 and 00:30:30
    if (minutes > 31) {
      wait_time = (61 - minutes) * 60 * 1000 - (30 * 1000);
    } else {
      wait_time = (31 - minutes) * 60 * 1000 - (30 * 1000);
    }
    wait_sync = setTimeout(runInterval, wait_time);
    ws4redis = new WS4Redis({
      uri: websocket_root+'repeating_tasks?subscribe-broadcast&publish-broadcast&echo',
      receive_message: onReceiveItemWS,
      heartbeat_msg: "--heartbeat--"
    });
  }

  function stopInterval() {
    if (wait_sync) {
      wait_sync = clearTimeout(wait_sync);
    }
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    try {
      ws4redis.close();
    } catch(e) {

    }
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
  this.update = update;
}

var tasks_today, tasks_tomorrow, tasks_all;

$(document).ready(function() {
  tasks_today = new RepeatingTasks("#today .repeating-tasks .fa-ul", "today");
  tasks_tomorrow = new RepeatingTasks("#tomorrow .repeating-tasks .fa-ul", "tomorrow");
  tasks_all = new RepeatingTasks("#repeating-tasks-all .fa-ul", "all");
  tasks_today.startInterval();
  tasks_tomorrow.startInterval();
  tasks_all.startInterval();
  $("#confirm-repeating-task .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
  $("#confirm-repeating-task .yes").on("click", function () {
    $.get("/homecontroller/repeating_tasks/done/"+$(this).parent().parent().parent().data("id"), function() {
      tasks_today.update();
      tasks_tomorrow.update();
      tasks_all.update();
    });
    switchVisibleContent("#main-content");
  });
  $("#confirm-repeating-task .cancel").on("click", function () {
    switchVisibleContent("#main-content");
  });

  $("#main-button-box .repeating").on("click", function() {
    switchVisibleContent("#repeating-tasks-all");
  });

  $("#repeating-tasks-all .close").on("click", function() {
    switchVisibleContent("#main-content");
  });

});
