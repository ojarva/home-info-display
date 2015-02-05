var Birthdays = function(elem, use_date, options) {
  options = options || {};
  options.interval = options.interval || 1800000; // 30min
  options.showdate = options.showdate || false;
  options.maxitems = options.maxitems || 100000;
  var parent_elem = $(elem), this_date = use_date, update_interval, wait_sync, current_item = 0, items_in_current = 0;
  parent_elem = parent_elem.slice(current_item, 1);

  function clearDates() {
    $(parent_elem).children().remove();
  }

  function compareBirthdays(a,b) {
    if (a.birthday_sort < b.birthday_sort) {
      return -1;
    }
    if (a.birthday_sort > b.birthday_sort) {
      return 1;
    }
    return 0;
  }

  function update() {
    $.get("/homecontroller/birthdays/get_json/"+this_date, function(data) {
      clearDates();
      now = moment().subtract(1, "days");
      m = now.month();
      if (m < 10) {
        m = "0"+m;
      }
      d = now.date();
      if (d < 10) {
        d = "0"+d;
      }
      now_str = ""+m+d;
      data_sortable = []
      $.each(data, function() {
        a = moment(this.fields.birthday);
        m = a.month();
        if (m < 10) {
          m = "0"+m;
        }
        d = a.date();
        if (d < 10) {
          d = "0"+d;
        }
        this.birthday_moment = a;
        prefix = "0";
        this.next_year = false;
        if (""+m+d < now_str) {
          prefix = "1";
          this.next_year = true;
        }
        this.birthday_sort = prefix+m+d;
        data_sortable.push(this);
      });
      data_sortable.sort(compareBirthdays);


      $.each(data_sortable, function() {
        name = this.fields.name;
        if (this.fields.nickname) {
          name = this.fields.nickname;
        }
        var age = "";
        if (this.fields.valid_year) {
          b = moment(this.birthday_moment);
          b = b.year(now.year());
          if (this.next_year) {
            b = b.add(1, "year");
          }
          age = (" ("+this.birthday_moment.from(b)+")").replace(" sitten", "");
        }
        var date = "";
        if (options.showdate) {
          date = " - "+this.birthday_moment.date()+"."+(this.birthday_moment.month()+1)+".";
          if (this.fields.valid_year) {
            date += this.birthday_moment.year();
          }
        }
        if (items_in_current > options.maxitems) {
          current_item += 1;
          parent_elem = $(elem).slice(current_item, current_item + 1);
          items_in_current = 0;
        }
        items_in_current += 1;
        parent_elem.append("<li><i class='fa-li fa fa-birthday-cake'></i> "+name+date+age+"</li>");
      })
    });
  }

  function runInterval() {
    update_interval = setInterval(update, options.interval);
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

var birthdays_today, birthdays_tomorrow, birthdays_all;

$(document).ready(function() {
  birthdays_today = new Birthdays("#today .birthdays .fa-ul", "today");
  birthdays_tomorrow = new Birthdays("#tomorrow .birthdays .fa-ul", "tomorrow");
  birthdays_all = new Birthdays("#birthdays-list-all .fa-ul", "all", {interval: 60*60*1000, showdate: true, maxitems: 38});
  birthdays_today.startInterval();
  birthdays_tomorrow.startInterval();
  birthdays_all.startInterval();
  $("#main-button-box .birthdays").on("click", function () {
    switchVisibleContent("#birthdays-list-all");
  });
  $("#birthdays-list-all .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
