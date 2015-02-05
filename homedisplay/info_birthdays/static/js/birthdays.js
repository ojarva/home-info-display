var Birthdays = function(elem, use_date) {
  var parent_elem = $(elem), this_date = use_date, update_interval, wait_sync;

  function clearDates() {
    $(parent_elem).children().remove();
  }

  function update() {
    $.get("/homecontroller/birthdays/get_json/"+this_date, function(data) {
      clearDates();
      $.each(data, function() {
        name = this.fields.name;
        if (this.fields.nickname) {
          name = this.fields.nickname;
        }
        var age = "";
        if (this.fields.valid_year) {
          age = (" ("+moment(this.fields.birthday).fromNow()+")").replace(" sitten", "");
        }
        $(parent_elem).append("<li><i class='fa-li fa fa-birthday-cake'></i> "+name+age+"</li>");
        console.log(this);
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

var birthdays_today, birthdays_tomorrow;

$(document).ready(function() {
  birthdays_today = new Birthdays("#today .birthdays .fa-ul", "today");
  birthdays_tomorrow = new Birthdays("#tomorrow .birthdays .fa-ul", "tomorrow");
  birthdays_today.startInterval();
  birthdays_tomorrow.startInterval();
});
