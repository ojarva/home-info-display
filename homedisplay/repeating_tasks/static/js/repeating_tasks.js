var RepeatingTasks = function(elem, use_date) {
  var parent_elem = $(elem), this_date = use_date, update_interval, wait_sync;

  function clearTasks() {
    $(parent_elem).children().remove();
  }

  function update() {
    $.get("/homecontroller/repeating_tasks/get_json/"+this_date, function(data) {
      clearTasks();
      $.each(data, function() {
        console.log(this);
        overdue_by = "";
        console.log(this.fields.last_completed_at);
        if (this.fields.last_completed_at) {
          diff = moment(this.fields.last_completed_at).add(this.fields.repeat_every_n_seconds, "seconds");
          overdue_by = " ("+diff.fromNow()+")";
        }
        $(parent_elem).append("<li><i class='fa-li fa fa-times-circle'></i> "+this.fields.title+overdue_by+"</li>");
      })
    });
  }

  function runInterval() {
    update_interval = setInterval(update, 1800000); // 30min
  }

  function startInterval() {
    stopInterval();
    update();
    now = new Date();
    minutes = now.getMinutes();
    // Sync intervals to run at 00:00:30 and 00:30:30
    if (minutes > 31) {
      wait_time = (61 - minutes) * 60 * 1000 - (30 * 1000);
    } else {
      wait_time = (31 - minutes) * 60 * 1000 - (30 * 1000);
    }
    wait_sync = setTimeout(runInterval, wait_time);
  }

  function stopInterval() {
    if (wait_sync) {
      wait_sync = clearTimeout(wait_sync);
    }
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
}

var tasks_today, tasks_tomorrow;

$(document).ready(function() {
  tasks_today = new RepeatingTasks("#today .repeating-tasks .fa-ul", "today");
  tasks_tomorrow = new RepeatingTasks("#tomorrow .repeating-tasks .fa-ul", "tomorrow");
  tasks_today.startInterval();
  tasks_tomorrow.startInterval();
});
