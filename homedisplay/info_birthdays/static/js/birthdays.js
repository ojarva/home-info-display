var Birthdays = function(elem, use_date, options) {
  "use strict";
  options = options || {};
  options.showdate = options.showdate || false;
  options.maxitems = options.maxitems || 100000;
  var parent_elem = jq(elem), this_date = use_date, update_interval, current_item = 0, items_in_current = 0;
  parent_elem = parent_elem.slice(0, 1);

  function onReceiveItemWS(message) {
    processData(message);
  }

  function clearDates() {
    jq(elem).find("li").remove();
    items_in_current = 0;
    current_item = 0;
    parent_elem = jq(elem).slice(current_item, 1);
  }

  function compareBirthdays(a, b) {
    if (a.birthday_sort < b.birthday_sort) {
      return -1;
    }
    if (a.birthday_sort > b.birthday_sort) {
      return 1;
    }
    return 0;
  }

  function formatSortString(da) {
    da = moment(da);
    var m = da.month();
    if (m < 10) {
      m = "0" + m;
    }
    var d = da.date();
    if (d < 10) {
      d = "0" + d;
    }
    return "" + m + d;
  }

  function processData(data) {
    clearDates();
    var now, now_str, data_sortable = [];
    now = clock.getMoment().subtract(1, "days");
    now_str = formatSortString(now);
    jq.each(data, function() {
      var a, sort_string, prefix;
      a = moment(this.fields.birthday);
      sort_string = formatSortString(a);
      this.birthday_moment = a;
      prefix = "0";
      this.next_year = false;
      if (sort_string < now_str) {
        prefix = "1";
        this.next_year = true;
      }
      this.birthday_sort = prefix + sort_string;
      data_sortable.push(this);
    });
    data_sortable.sort(compareBirthdays);


    jq.each(data_sortable, function() {
      var name = this.fields.name, age = "", b, date = "", extra = "";
      if (this.fields.nickname) {
        name = this.fields.nickname;
      }
      if (this.fields.valid_year) {
        b = moment(this.birthday_moment);
        b = b.year(now.year());
        if (this.next_year) {
          b = b.add(1, "year");
        }
        age = (" (" + this.birthday_moment.from(b) + ")").replace(" sitten", "");
      }
      if (options.showdate) {
        date = " - " + this.birthday_moment.date() + "." + (this.birthday_moment.month() + 1) + ".";
        if (this.fields.valid_year) {
          date += this.birthday_moment.year();
        }
      }
      if (items_in_current > options.maxitems) {
        current_item += 1;
        if (current_item > 3) {
          return false;
        }
        parent_elem = jq(elem).slice(current_item, current_item + 1);
        items_in_current = 0;
      }
      items_in_current += 1;
      if (this_date === "tomorrow") {
        extra = " (huomenna)";
      }
      parent_elem.append("<li><i class='fa-li fa fa-birthday-cake'></i> " + name + date + age + extra + "</li>");
    });
  }

  function update() {
    jq.get("/homecontroller/birthdays/get_json/" + this_date, function(data) {
      processData(data);
    });
  }

  function startInterval() {
    update();
    ws_generic.register("birthdays_" + this_date, onReceiveItemWS);
    ge_refresh.register("birthdays_" + this_date, update);
    ge_intervals.register("birthdays_" + this_date, "daily", update);
  }

  function stopInterval() {
    ws_generic.deRegister("birthdays_" + this_date);
    ge_refresh.deRegister("birthdays_" + this_date);
    ge_intervals.deRegister("birthdays_" + this_date, "daily");
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var birthdays_today, birthdays_tomorrow, birthdays_all;

jq(document).ready(function() {
  "use strict";
  birthdays_today = new Birthdays("#today .list-birthdays .fa-ul", "today");
  birthdays_tomorrow = new Birthdays("#tomorrow .list-birthdays .fa-ul", "tomorrow");
  birthdays_all = new Birthdays("#birthdays-list-all .fa-ul", "all", {interval: 60 * 60 * 1000, showdate: true, maxitems: 45});
  birthdays_today.startInterval();
  birthdays_tomorrow.startInterval();
  birthdays_all.startInterval();
  jq(".main-button-box .birthdays").on("click", function () {
    content_switch.switchContent("#birthdays-list-all");
  });
  jq("#birthdays-list-all .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
