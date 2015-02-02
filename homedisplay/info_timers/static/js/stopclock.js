
var Stopclock = function(parent_elem, options) {
  var start, interval, running = false, id_uniq = Math.random().toString().replace(".", ""), id;
  options = options || {};
  options.delay = options.delay || 100;

  function create() {
    $(parent_elem).append("<div class='row timer-item' id='stopclock-"+id_uniq+"'>"+
    "<div class='col-md-8 stopclock timer-main center-content stopclock-content'>"+
    "00:00:00.0"+
    "</div>"+
    "<div class='col-md-2 timer-stop timer-control animate-click stopclock-stop'>"+
    "<i class='fa fa-stop'></i>"+
    "</div>"+
    "<div class='col-md-2 timer-refresh timer-control animate-click stopclock-restart'>"+
    "<i class='fa fa-refresh'></i>"+
    "</div>"+
    "</div>");
    restart();

    $("#stopclock-"+id_uniq+" .stopclock-stop").click(function() {
      stop();
    });
    $("#stopclock-"+id_uniq+" .stopclock-restart").click(function () {
      restart();
    });
/*    $("#stopclock-stop").click(function () {
      console.log(stopclock_run);
      stopclock_run.stop();
    });
    $("#stopclock-restart").click(function () {
      stopclock_run.restart();
    });

    restart();
    $.post("/timer/create", {name: "Stopclock"}, function(data) {
      id = data.id;
    });*/
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
    var diff = (now - start) / 1000;
    var hours = Math.floor(diff / 3600);
    diff = diff - hours * 3600;
    var minutes = Math.floor(diff / 60);
    diff = diff - minutes * 60;
    var seconds = Math.floor(diff);
    var msec = diff - seconds;
    var timer = zeroPad(hours, 2) + ":"+zeroPad(minutes, 2)+":"+zeroPad(seconds, 2)+"."+(String(Math.round(msec*10))+"00").substr(0,1);
    $("#stopclock-"+id_uniq+" .stopclock-content").html(timer);
  }

  function restart() {
    start = new Date();
    if (interval) {
      clearInterval(interval);
      $("#stopclock-"+id_uniq).effect("highlight", {color: "#006600"}, 500);

    }
    running = true;
    interval = setInterval(update, options.delay);
    update();
    $("#stopclock-"+id_uniq+" .stopclock-stop i").removeClass("fa-trash").addClass("fa-stop");
  }

  function stop() {
    if ($("#stopclock-"+id_uniq+" .stopclock-stop i").hasClass("fa-trash")) {
      // Delete counter
      $("#stopclock-"+id_uniq).slideUp("slow");
      $("#stopclock-"+id_uniq).remove();
      // TODO: update backend
    } else {
      $("#stopclock-"+id_uniq).effect("highlight", {color: "#cc0000"}, 500);

      running = false;
      if (interval) {
        clearInterval(interval);
      }
      $("#stopclock-"+id_uniq+" .stopclock-stop i").removeClass("fa-stop").addClass("fa-trash");
    }
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

$(document).ready(function () {
  $("#add-stopclock").click(function () {
    var stopclock_run = new Stopclock("#stopclock-holder");
  });
//  setInterval(stopclock_run.refresh_from_server, 5000);
});
