var Timer = function(parent_elem, options) {
  var timer_type,
      created_by_backend = false,
      start_time,
      update_interval,
      backend_interval,
      alarm_interval,
      ws4redis,
      running = false, id_uniq = Math.random().toString().replace(".", ""), id;

  var this_elem;
  options = options || {};
  options.delay = options.delay || 100;
  options.backend_interval = options.backend_interval || 5*60*1000;

  if (options.id) {
    setId(options.id);
    created_by_backend = true;
  }
  if (options.start_time) {
    start_time = options.start_time;
  }
  if (options.duration) {
    timer_type = "timer";
  } else {
    timer_type = "stopclock";
  }

  function onReceiveItemWS(message) {
    console.log(id,"received message",message);
    source = "backend";
    if (message == "stop") {
      stopItem(source);
    } else if (message == "delete") {
      deleteItem(source);
    } else if (message == "restart") {
      restartItem(source);
    } else if (message == "start") {
      startItem(source);
    } else {
      console.log("Unknown per-item WS message: ", message);
    }
  }

  function setId(new_id) {
    // Set backend id to local object.
    id = new_id;
    timers.addTimerId(id);
    ws4redis = new WS4Redis({
      uri: websocket_root+'timer-'+id+'?subscribe-broadcast&publish-broadcast&echo',
      receive_message: onReceiveItemWS,
      heartbeat_msg: "--heartbeat--"
    });
  }

  function getId() {
    return id;
  }

  function create() {
    // Creates HTML elements and starts timer.
    if (timer_type == "timer") {
      $(parent_elem).append("<div class='row timer-item' style='display:none' id='timer-"+id_uniq+"'>"+
      " <div class='col-md-8'>"+
      "   <div class='timer-info'>"+
      "     "+options.name+" <span style='float: right' class='timer-timeleft'>---</span>"+
      "   </div>"+
      "   <div class='progress hidden-xs hidden-sm'>"+
      "    <div class='progress-bar' role='progressbar' aria-valuenow='100' aria-valuemin='0' aria-valuemax='100' style='width:100%'>"+
      "    </div>"+
      "   </div>"+
      " </div>"+
      " <div class='col-md-2 timer-stop timer-control animate-click'>"+
      "   <i class='fa fa-trash'></i>"+
      " </div>"+
      " <div class='col-md-2 timer-restart timer-control animate-click'>"+
      "   <i class='fa fa-refresh'></i>"+
      " </div>"+
      "</div>");
      this_elem = $("#timer-"+id_uniq);
      this_elem.find(".timer-stop").click(function() {
        deleteItem("ui");
      });
      this_elem.find(".timer-restart").click(function () {
        restartItem("ui");
      });

    } else {
      $(parent_elem).append("<div class='row timer-item' style='display:none' id='timer-"+id_uniq+"'>"+
      " <div class='col-md-8 stopclock timer-main center-content stopclock-content'>"+
      "   00:00:00.0"+
      " </div>"+
      " <div class='col-md-2 timer-control animate-click stopclock-stop'>"+
      "   <i class='fa fa-stop'></i>"+
      " </div>"+
      " <div class='col-md-2 timer-control animate-click stopclock-restart'>"+
      "   <i class='fa fa-refresh'></i>"+
      " </div>"+
      "</div>");

      this_elem = $("#timer-"+id_uniq);
      this_elem.find(".stopclock-stop").click(function() {
        stopItem("ui");
      });
      this_elem.find(".stopclock-restart").click(function () {
        restartItem("ui");
      });
    }
    this_elem.data("original-bg-color", this_elem.css("background-color"));

    this_elem.stop(true).slideDown("fast");

    if (created_by_backend) {
      this_elem.addClass("timer-backend-id-"+id);
      if (options.running) {
        startItem("backend");
      } else {
        stopItem("backend");
      }
    } else {
      restartItem("ui");
      $.post("/homecontroller/timer/create", {name: options.name, duration: options.duration}, function(data) {
        setId(data[0].pk);
        this_elem.addClass("timer-backend-id-" + data[0].pk);
        start_time = new Date(data[0].fields.start_time)
      });
    }
  }
  create();

  // Helper functions
  // ----------------
  function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
  }

  function update_timer_content(diff, prefix) {
    var hours = Math.floor(diff / 3600);
    diff = diff - hours * 3600;
    var minutes = Math.floor(diff / 60);
    diff = diff - minutes * 60;
    var seconds = Math.floor(diff);
    var msec = diff - seconds;
    var timer = prefix+zeroPad(hours, 2) + ":"+zeroPad(minutes, 2)+":"+zeroPad(seconds, 2)+"."+(String(Math.round(msec*10))+"00").substr(0,1);
    // TODO: timer/stopclock
    if (timer_type == "timer") {
      this_elem.find(".timer-timeleft").html(timer);
    } else {
      this_elem.find(".stopclock-content").html(timer);
    }
  }

  function stopItem(source) {
    //TODO: support for timers
    if (source != "backend" && this_elem.find(".stopclock-stop i").hasClass("fa-trash")) {
      // Delete stopwatch only if event was initiated by user *and* stopwatch was already stopped.
      deleteItem("ui");
    } else {
      this_elem.stop(true).css("background-color", this_elem.data("original-bg-color")).effect("highlight", {color: "#cc0000"}, 500);

      running = false;
      clearItemIntervals();
      this_elem.find(".stopclock-stop i").removeClass("fa-stop").addClass("fa-trash");
      if (source != "backend") {
        $.get("/homecontroller/timer/stop/"+id, function (data) {
          diff = ((new Date(data[0].fields.stopped_at)) - (new Date(data[0].fields.start_time))) / 1000;
          update_timer_content(diff, "");
        });
      } else if (options.stopped_at) {
        diff = (new Date(options.stopped_at) - start_time) / 1000;
        update_timer_content(diff, "");
      }
    }
  }

  function update() {
    if (!running) {
      return;
    }
    var now = new Date();
    var prefix = "";
    if (timer_type == "timer") {
      var diff = parseInt(options.duration) - (now - start_time) / 1000;
      var percent = Math.round((parseFloat(diff) / parseFloat(options.duration)) * 100);
      if (percent > 100) {
        percent = 100;
      }
      if (diff < 0) {
        prefix = "-";
        diff *= -1;
      }
      if (percent > 0) {
        this_elem.find(".progress-bar").css("width", percent+"%").removeClass("progress-bar-danger").addClass("progress-bar-success");
        this_elem.removeClass("timer-overtime");
      } else {
        this_elem.find(".progress-bar").removeClass("progress-bar-success").addClass("progress-bar-danger").css("width", "100%");
        this_elem.addClass("timer-overtime");
        // TODO: play alarm
      }
    } else if (timer_type == "stopclock"){
      var diff = (now - start_time) / 1000;
    }
    update_timer_content(diff, prefix);
  }

  function clearItemIntervals() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
    if (alarm_interval) {
      alarm_interval = clearInterval(alarm_interval);
    }
  }

  function startItem(source) {
    clearItemIntervals();
    running = true;
    update(); // Immediately run first update
    update_interval = setInterval(update, options.delay);
    backend_interval = setInterval(refreshFromBackend, options.backend_interval);
    this_elem.data("start-timestamp", start_time);
    if (timer_type == "timer") {
      this_elem.data("end-timestamp", (start_time.getTime()/1000) + options.duration);
    }
    timers.sortTimers();
    if (source != "backend" && id) {
      $.get("/homecontroller/timer/start/"+id, function(data) {
        //TODO
      });
    }
  }

  function refreshFromBackend() {
    if (id) { // Don't refresh if no data is available.
      $.ajax({
        url: "/homecontroller/timer/get/"+id,
        success: function (data) {
          start_time = new Date(data[0].fields.start_time);
          if (data[0].fields.running) {
            if (!running) {
              startItem("backend");
            }
          } else {
            if (running) {
              stopItem("backend");
            }
          }
        },
        statusCode: {
          404: function () {
            deleteItem("backend");
          }
        }
      });
    }
  }


  function restartItem(source) {
    if (running) {
      this_elem.stop(true).css("background-color", this_elem.data("original-bg-color")).effect("highlight", {color: "#006600"}, 500);
    }
    if (source != "backend") {
      start_time = new Date();
    }
    startItem(source);
    if (source != "backend" && id) {
      $.get("/homecontroller/timer/restart/"+id, function (data) {
        start_time = new Date(data[0].fields.start_time);
      });
    }
  }

  function deleteItem(item_source) {
    this_elem.slideUp("fast", function () { $(this).remove(); });
    clearItemIntervals();
    if (backend_interval) {
      backend_interval = clearInterval(backend_interval);
    }
    if (item_source != "backend" && id) {
      $.get("/homecontroller/timer/delete/"+id, function(data) {
      });
    }
    try {
      ws4redis.close(); // Clean up WS connections
    } catch (e) {

    }
  }

  this.deleteItem = deleteItem;
  this.restartItem = restartItem;
  this.startItem = startItem;
  this.getId = getId;
};

var Timers = function(options) {
  options = options || {};
  options.update_interval = options.update_interval || 3 * 60 * 1000;
  var timer_holder = options.timer_holder || "#timer-holder";
  var stopclock_holder = options.stopclock_holder || "#stopclock-holder";
  var created_timer_items = [];

  function refreshFromServer() {
    $.getJSON("/homecontroller/timer/list", function(data) {
      $.each(data, function() {
        var id = this.pk;
        if (!hasTimer(id)) {
          if (this.fields.duration === null) {
          // if data.duration is not null, it's timer, not countdown
            var timer_run = new Timer(stopclock_holder, {"name": this.fields.name, "start_time": new Date(this.fields.start_time), "running": this.fields.running, "id": this.pk, stopped_at: this.fields.stopped_at});
          } else {
            var timer_run = new Timer(timer_holder, {"name": this.fields.name, "duration": this.fields.duration, "start_time": new Date(this.fields.start_time), "running": this.fields.running, "id": this.pk, stopped_at: this.fields.stopped_at});
          }
        }
      });
    });
  }

  function addTimerId(id) {
    created_timer_items.push(id);
  }

  function hasTimer(id) {
    currently_running = $(".timer-backend-id-"+id);
    if (id in created_timer_items) {
      return false;
    }
    if (currently_running.length == 0) {
      return false;
    } else {
      return true;
    }
  }

  function sortTimers() {
    var items = $(timer_holder).find(".timer-item");
    items.detach().sort(function(a,b) {
      var astts = $(a).data('end-timestamp');
      var bstts = $(b).data('end-timestamp')
      return (astts > bstts) ? (astts > bstts) ? 1 : 0 : -1;
    });
    $(timer_holder).append(items);

    var items = $(stopclock_holder).find(".timer-item");
    items.detach().sort(function(a,b) {
      var astts = $(a).data('start-timestamp');
      var bstts = $(b).data('start-timestamp')
      return (astts > bstts) ? (astts > bstts) ? 1 : 0 : -1;
    });
    $(stopclock_holder).append(items);
  }

  function onReceiveWS(message) {
    /* Ugly hack: WS message arrives before HTTP response.
       This leads to duplicate timer items, as originally
       added timer does not have ID yet. */
   console.log("Timer global: received message", message);
    setTimeout(function () {
      if (message.substring(0, 7) == "create-") {
        var data = JSON.parse(message.substring(7))[0];
        if (!hasTimer(data.pk)) {
          if (data.fields.duration === null) {
            // if data.duration is not null, it's timer, not countdown
            var timer_run = new Timer(stopclock_holder, {"name": data.fields.name, "start_time": new Date(data.fields.start_time), "running": data.fields.running, "id": data.pk, stopped_at: data.fields.stopped_at});
          } else {
            var timer_run = new Timer(timer_holder, {"name": data.fields.name, "duration": data.fields.duration, "start_time": new Date(data.fields.start_time), "running": data.fields.running, "id": data.pk, stopped_at: data.fields.stopped_at});
          }
        }
      }
    }, 1000);
  }

  var ws4redis = new WS4Redis({
    uri: websocket_root+'timers?subscribe-broadcast&publish-broadcast&echo',
    receive_message: onReceiveWS,
    heartbeat_msg: "--heartbeat--"
  });

  $(".add-timer").click(function () {
    var timer_run = new Timer(timer_holder, {"name": $(this).data("name"), "duration": $(this).data("duration")});
  });
  $(".add-stopclock").click(function () {
    var timer_run = new Timer(stopclock_holder, {"name": "Ajastin"});
  });

  refreshFromServer();
  setInterval(refreshFromServer, options.update_interval);

  this.sortTimers = sortTimers;
  this.hasTimer = hasTimer;
  this.refreshFromServer = refreshFromServer;
  this.addTimerId = addTimerId;
};

var timers;

$(document).ready(function () {
  timers = new Timers({stopclock_holder: "#stopclock-holder", timer_holder: "#timer-holder"});
});
