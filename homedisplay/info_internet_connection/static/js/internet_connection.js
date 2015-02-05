var RefreshInternet = function() {
  var ws4redis, update_interval;

  function update() {
    $.get("/homecontroller/internet_connection/status", function (data) {
      var data = data[0];
      if (typeof data == "undefined") {
        console.log("!!! No internet connection information available");
        return;
      }
      var output = $("#internet-connection");
      var cs = data.fields.connect_status;
      var cs_out;
      if (cs == "connected") {
        cs_out = "<i class='fa fa-check-circle success-message'></i>";
      } else if (cs == "connecting") {
        cs_out = "<i class='fa fa-spin fa-cog warning-message'></i>";
      } else {
        cs_out = "<i class='fa fa-times error-message'></i>";
      }
      output.find(".connected").html(cs_out);
      output.find(".mode").html(data.fields.mode);
      output.find(".signal").html("<i class='fa fa-signal'></i> "+data.fields.signal+"/5");
      var data_moment = moment(data.fields.timestamp);
      output.find(".age").html("("+data_moment.fromNow()+")");
    });
  }

  function onReceiveItemWS(message) {
    if (message == "updated") {
      console.log("internet: backend requests update");
      update();
    }
  }

  function startInterval() {
    stopInterval();
    update();
    update_interval = setInterval(update, 1800000);
    ws4redis = new WS4Redis({
      uri: websocket_root+'internet?subscribe-broadcast&publish-broadcast&echo',
      receive_message: onReceiveItemWS,
      heartbeat_msg: "--heartbeat--"
    });
  }

  function stopInterval() {
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
};

var refresh_internet;
$(document).ready(function() {
  refresh_internet = new RefreshInternet();
  refresh_internet.startInterval();

  $("#internet-connection").on("click", function() {
    var charts = [["idler", "Internet/idler_last_10800.png"],
                  ["Google", "Internet/google_last_10800.png"],
                  ["Saunalahti", "Internet/saunalahti_last_10800.png"],
                  ["Funet", "Internet/funet_last_10800.png"],
                  ["idler", "Internet/idler_last_108000.png"],
                  ["Google", "Internet/google_last_108000.png"],
                  ["Saunalahti", "Internet/saunalahti_last_108000.png"],
                  ["Funet", "Internet/funet_last_108000.png"]
                  ];
    var content = "";
    var timestamp = new Date() - 0;
    $.each(charts, function() {
      content += "<div class='smokeping-chart'><h4>"+this[0]+"</h4><img src='/smokeping/images/"+this[1]+"?"+timestamp+"'></div>";
    });
    $("#internet-connection-modal .smokeping-charts").html(content);
    switchVisibleContent("#internet-connection-modal");
  });

  $("#internet-connection-modal .close").on("click", function () {
    switchVisibleContent("#main-content");
  });
});
