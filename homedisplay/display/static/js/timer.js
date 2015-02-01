// Shamelessly copied from http://stackoverflow.com/a/13194087/592174
var beep = (function () {
  var ctx = new(window.audioContext || window.webkitAudioContext);
  return function (duration, type, finishedCallback) {

    duration = +duration;

    // Only 0-4 are valid types.
    type = (type % 5) || 0;

    if (typeof finishedCallback != "function") {
      finishedCallback = function () {};
    }

    var osc = ctx.createOscillator();

    osc.type = type;

    osc.connect(ctx.destination);
    osc.noteOn(0);

    setTimeout(function () {
      osc.noteOff(0);
      finishedCallback();
    }, duration);

  };
})();

var Timer = function(parent_elem, options) {
  var start, interval, alarm_playing = false, alarm_interval, running = false, id_uniq = Math.random().toString().replace(".", ""), id;
  options = options || {};
  options.delay = options.delay || 100;

  function create() {
    $(parent_elem).append("<div class='row timer-item timer-item-even' style='display:none' id='timer-"+id_uniq+"'>"+
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
    restart();
    $("#timer-"+id_uniq).stop(true).slideDown("fast");

    $("#timer-"+id_uniq+" .timer-stop").click(function() {
      stop();
    });
    $("#timer-"+id_uniq+" .timer-restart").click(function () {
      restart();
    });
  }
  create();

  function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
  }

  function update() {
    if (!running) {
      return;
    }
    var now = new Date();
    var diff = parseInt(options.duration) - (now - start) / 1000;

    var percent = Math.round((parseFloat(diff) / parseFloat(options.duration)) * 100);
    if (percent > 100) {
      percent = 100;
    }
    var prefix = "";
    if (diff < 0) {
      prefix = "-";
      diff *= -1;
    }
    if (percent > 0) {
      $("#timer-"+id_uniq+" .progress-bar").css("width", percent+"%").removeClass("progress-bar-danger").addClass("progress-bar-success");
      $("#timer-"+id_uniq).removeClass("timer-overtime");
    } else {
      $("#timer-"+id_uniq+" .progress-bar").removeClass("progress-bar-success").addClass("progress-bar-danger").css("width", "100%");
      $("#timer-"+id_uniq).addClass("timer-overtime");
      if (!alarm_playing) {
        alarm_playing = true;
        play_alarm();
        if (alarm_interval) {
          clearInterval(alarm_interval);
        }
        alarm_interval = setInterval(play_alarm, 30000);
      }


    }
    var hours = Math.floor(diff / 3600);
    diff = diff - hours * 3600;
    var minutes = Math.floor(diff / 60);
    diff = diff - minutes * 60;
    var seconds = Math.floor(diff);
    var msec = diff - seconds;
    var timer = prefix+zeroPad(hours, 2) + ":"+zeroPad(minutes, 2)+":"+zeroPad(seconds, 2)+"."+(String(Math.round(msec*10))+"00").substr(0,1);
    $("#timer-"+id_uniq+" .timer-timeleft").html(timer);
  }

  function play_alarm() {

  }


  function restart() {
    start = new Date();
    if (interval) {
      clearInterval(interval);
      $("#timer-"+id_uniq).stop(true).effect("highlight", {color: "#006600"}, 500);
    }
    if (alarm_interval) {
      clearInterval(alarm_interval);
    }
    alarm_playing = false;

    running = true;
    interval = setInterval(update, options.delay);
    update();
    $("#timer-"+id_uniq).data("end-timestamp", (start.getTime()/1000) + options.duration);
    sort_timers();
    // TODO: update backend
  }

  function stop() {
    $("#timer-"+id_uniq).slideUp("fast", function () { $(this).remove(); });
    if (interval) {
      clearInterval(interval);
    }
    if (alarm_interval) {
      clearInterval(alarm_interval);
    }
    alarm_playing = false;

    // TODO: update backend
  }

  this.stop = stop;
  this.restart = restart;
};


function refresh_from_server() {
  $.getJSON("/timers/list", function(data) {
    $.each(data, function() {
      if (data.duration === null) {
        // if data.duration is not null, it's timer, not countdown

      }
    });
  });
}

function sort_timers() {
  var items = $("#timer-holder .timer-item");
  items.detach().sort(function(a,b) {
    var astts = $(a).data('end-timestamp');
    var bstts = $(b).data('end-timestamp')
    return (astts > bstts) ? (astts > bstts) ? 1 : 0 : -1;
  });
  $("#timer-holder").append(items);
}

$(document).ready(function () {
  $(".add-timer").click(function () {
    var timer_run = new Timer("#timer-holder", {"name": $(this).data("name"), "duration": $(this).data("duration")});
  });

});
