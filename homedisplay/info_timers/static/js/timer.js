var created_timer_items = [];

var Timer = function(parent_elem, options) {
  var timer_type, created_backend = false, start, interval, backend_interval, alarm_interval, running = false, id_uniq = Math.random().toString().replace(".", ""), id;
  var this_elem;
  options = options || {};
  options.delay = options.delay || 100;
  if (options.id) {
    setId(options.id);
    created_backend = true;
  }
  if (options.start_time) {
    start = options.start_time;
  }
  if (options.duration) {
    timer_type = "timer";
  } else {
    timer_type = "stopclock";
  }

  function onReceiveItemWS(message) {
    console.log("onReceiveItemWS", id, message);
    if (message == "stop") {
      stop("backend");
    } else if (message == "delete") {
      deleteItem("backend");
    } else if (message == "restart") {
      restart("backend");
    } else if (message == "start") {
      startItem("backend");
    } else {
      console.log("Unknown per-item WS message: ", message);
    }
  }

  function setId(new_id) {
    // Set backend id to local object.
    id = new_id;
    created_timer_items.push(id);
    ws4redis = WS4Redis({
      //TODO
      uri: 'ws://localhost:8000/ws/timer-'+id+'?subscribe-broadcast&publish-broadcast&echo',
      receive_message: onReceiveItemWS,
      heartbeat_msg: "--heartbeat--"
    });
  }

  function create() {
    // Creates HTML elements and starts timer.
    if (timer_type == "timer") {
      $(parent_elem).append("<div class='row timer-item' style='display:none' id='timer-"+id_uniq+"'>"+
      " <div class='col-md-8'>"+
      "   <div class='timer-info'>"+
      "     "+options.name+" <span style='float: right' class='timer-timeleft'>---</span>"+
      "   </div>"+
      "   <div class='progress'>"+
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
        deleteItem();
      });
      this_elem.find(".timer-restart").click(function () {
        restart();
      });

    } else {
      $(parent_elem).append("<div class='row timer-item' id='stopclock-"+id_uniq+"'>"+
      "<div class='col-md-8 stopclock timer-main center-content stopclock-content'>"+
      "00:00:00.0"+
      "</div>"+
      "<div class='col-md-2 timer-control animate-click stopclock-stop'>"+
      "<i class='fa fa-stop'></i>"+
      "</div>"+
      "<div class='col-md-2 timer-control animate-click stopclock-restart'>"+
      "<i class='fa fa-refresh'></i>"+
      "</div>"+
      "</div>");
      this_elem = $("#stopclock-"+id_uniq);
      this_elem.find(".stopclock-stop").click(function() {
        stop();
      });
      this_elem.find(".stopclock-restart").click(function () {
        restart();
      });
    }

    this_elem.stop(true).slideDown("fast");

    if (created_backend) {
      this_elem.addClass("timer-backend-id-"+id);
      if (options.running) {
        startItem("backend");
      } else {
        stop("backend");
      }
    } else {
      restart();
      $.post("/homecontroller/timer/create", {name: options.name, duration: options.duration}, function(data) {
        setId(data[0].pk);
        this_elem.addClass("timer-backend-id-"+ id);
        start = new Date(data[0].fields.start_time)
      });
    }
  }
  create();

  function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
  }

  function stop(source) {
    //TODO: support for timers
    if (this_elem.find(".stopclock-stop i").hasClass("fa-trash")) {
      // Delete counter
      deleteItem();
    } else {
      this_elem.effect("highlight", {color: "#cc0000"}, 500);

      running = false;
      clearItemIntervals();
      this_elem.find(".stopclock-stop i").removeClass("fa-stop").addClass("fa-trash");
      if (source != "backend") {
        $.get("/homecontroller/timer/stop/"+id, function (data) {
          diff = ((new Date(data[0].fields.stopped_at)) - (new Date(data[0].fields.start_time))) / 1000;
          update_timer_content(diff, "");
        });
      } else if (options.stopped_at) {
        diff = (new Date(options.stopped_at) - start) / 1000;
        update_timer_content(diff, "");
      }
    }
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

  function update() {
    if (!running) {
      return;
    }
    var now = new Date();
    var prefix = "";
    if (timer_type == "timer") {
      var diff = parseInt(options.duration) - (now - start) / 1000;
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
      var diff = (now - start) / 1000;
    }
    update_timer_content(diff, prefix);
  }

  function clearItemIntervals() {
    if (interval) {
      clearInterval(interval);
    }
    if (alarm_interval) {
      clearInterval(alarm_interval);
    }
  }

  function startItem(source) {
    clearItemIntervals();
    running = true;
    interval = setInterval(update, options.delay);
    update();
    backend_interval = setInterval(refreshFromBackend, 15000);
    this_elem.data("start-timestamp", start);
    if (timer_type == "timer") {
      this_elem.data("end-timestamp", (start.getTime()/1000) + options.duration);
    }
    sort_timers();
    if (source != "backend") {
      $.get("/homecontroller/timer/start/"+id, function(data) {
        //TODO
      });
    }
  }

  function refreshFromBackend() {
    $.ajax({
      url: "/homecontroller/timer/get/"+id,
      success: function (data) {
        start = new Date(data[0].fields.start_time);
        if (data[0].fields.running) {
          if (!running) {
            startItem("backend");
          }
        } else {
          if (running) {
            //TODO: support for timers/stopclocks
            stop("backend");
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


  function restart(source) {
    if (interval) {
      this_elem.stop(true).effect("highlight", {color: "#006600"}, 500);
    }
    if (source != "backend") {
      start = new Date();
    }
    startItem(source);
    if (source != "backend") {
      $.get("/homecontroller/timer/restart/"+id, function (data) {
        start = new Date(data[0].fields.start_time);
      });
    }
  }

  function deleteItem(item_source) {
    this_elem.slideUp("fast", function () { $(this).remove(); });
    clearItemIntervals();
    ws4redis.close(); // Clean up WS connections
    if (backend_interval) {
      clearInterval(backend_interval);
    }
    if (item_source != "backend") {
      $.get("/homecontroller/timer/delete/"+id, function(data) {
      });
    }
  }

  this.deleteItem = deleteItem;
  this.restart = restart;
  this.startItem = startItem;
};


function refresh_timers_from_server() {
  $.getJSON("/homecontroller/timer/list", function(data) {
    $.each(data, function() {
      var id = this.pk;
      if (!hasTimer(id)) {
        if (this.fields.duration === null) {
        // if data.duration is not null, it's timer, not countdown
          var timer_run = new Timer("#stopclock-holder", {"name": this.fields.name, "start_time": new Date(this.fields.start_time), "running": this.fields.running, "id": this.pk, stopped_at: this.fields.stopped_at});
        } else {
          var timer_run = new Timer("#timer-holder", {"name": this.fields.name, "duration": this.fields.duration, "start_time": new Date(this.fields.start_time), "running": this.fields.running, "id": this.pk, stopped_at: this.fields.stopped_at});
        }
      }
    });
  });
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

function sort_timers() {
  var items = $("#timer-holder .timer-item");
  items.detach().sort(function(a,b) {
    var astts = $(a).data('end-timestamp');
    var bstts = $(b).data('end-timestamp')
    return (astts > bstts) ? (astts > bstts) ? 1 : 0 : -1;
  });
  $("#timer-holder").append(items);

  var items = $("#stopclock-holder .timer-item");
  items.detach().sort(function(a,b) {
    var astts = $(a).data('start-timestamp');
    var bstts = $(b).data('start-timestamp')
    return (astts > bstts) ? (astts > bstts) ? 1 : 0 : -1;
  });
  $("#stopclock-holder").append(items);
}

function onReceiveWS(message) {
  /* Ugly hack: WS message arrives before HTTP response.
     This leads to duplicate timer items, as originally
     added timer does not have ID yet. */
  setTimeout(function () {
    console.log("onReceiveWS", message);
    if (message.substring(0, 7) == "create-") {
      var data = JSON.parse(message.substring(7))[0];
      if (!hasTimer(data.pk)) {
        if (data.fields.duration === null) {
          // if data.duration is not null, it's timer, not countdown
          var timer_run = new Timer("#stopclock-holder", {"name": data.fields.name, "start_time": new Date(data.fields.start_time), "running": data.fields.running, "id": data.pk, stopped_at: data.fields.stopped_at});
        } else {
          var timer_run = new Timer("#timer-holder", {"name": data.fields.name, "duration": data.fields.duration, "start_time": new Date(data.fields.start_time), "running": data.fields.running, "id": data.pk, stopped_at: data.fields.stopped_at});
        }
      }
    }
  }, 1000);
}

var ws4redis;

$(document).ready(function () {
  ws4redis = WS4Redis({
    //TODO
    uri: 'ws://localhost:8000/ws/timers?subscribe-broadcast&publish-broadcast&echo',
    receive_message: onReceiveWS,
    heartbeat_msg: "--heartbeat--"
  });
  $(".add-timer").click(function () {
    var timer_run = new Timer("#timer-holder", {"name": $(this).data("name"), "duration": $(this).data("duration")});
  });
  $("#add-stopclock").click(function () {
    var timer_run = new Timer("#stopclock-holder", {"name": "Ajastin"});
  });
  refresh_timers_from_server();
  setInterval(refresh_timers_from_server, 10000);

});
