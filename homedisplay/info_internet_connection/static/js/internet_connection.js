var ShowRealtimePing = function(options) {
  "use strict";
  options = options || {};
  options.invalid_timeout = options.invalid_timeout || 10000;
  var container = jq(options.output), invalid_timeout;

  function noUpdates(warning_class) {
    warning_class = warning_class || "error";
    container.html("<i class='fa fa-times-circle " + warning_class + "-message'></i>");
  }
  function autoNoUpdates() {
    noUpdates("warning");
  }
  function update(message) {
    if (message === "no_pings") {
      noUpdates();
      return;
    }
    if (invalid_timeout) {
      invalid_timeout = clearTimeout(invalid_timeout);
    }
    container.html("<i class='fa fa-check-circle success-message'></i> " + (Math.round(parseFloat(message) * 10) / 10) + "ms");
    invalid_timeout = setTimeout(autoNoUpdates, options.invalid_timeout);
  }

  function startInterval() {
    ws_generic.register("ping", update);
  }

  function stopInterval() {
    ws_generic.deRegister("ping");
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var RefreshInternet = function(options) {
  "use strict";
  options = options || {};
  options.invalid_timeout = options.invalid_timeout || 2 * 60 * 1000;
  var update_timeout, output = jq(".internet-connection");

  function setSignal(level) {
    output.find(".signal-bars div").removeClass("active").addClass("inactive");
    for (var a = 1; a < level + 1; a++) {
      output.find(".signal-bars .signal-" + a).addClass("active").removeClass("inactive");
    }
  }

  function clearAutoNoUpdates() {
    if (update_timeout) {
      update_timeout = clearTimeout(update_timeout);
    }
  }

  function autoNoUpdates() {
    clearAutoNoUpdates();
    output.find(".signal-bars").slideUp();
    output.find(".signal-bars").data("is-hidden", true);
    output.find(".connected").html("<i class='fa fa-times warning-message'></i> Ei tietoja");
  }

  function processData(data) {
    if (typeof data === "undefined" || (data.status && data.status === "error")) {
      console.warn("!!! No internet connection information available");
      autoNoUpdates();
      return;
    }
    var signal_bars = output.find(".signal-bars");
    if (signal_bars.data("is-hidden")) {
      signal_bars.slideDown();
      signal_bars.data("is-hidden", false);
    }
    var cs = data.fields.connect_status;
    var cs_out;
    if (cs === "connected") {
      cs_out = "<i class='fa fa-check-circle success-message'></i>";
    } else if (cs === "connecting") {
      cs_out = "<i class='fa fa-spin fa-cog warning-message'></i>";
    } else {
      cs_out = "<i class='fa fa-times error-message'></i>";
    }
    output.find(".connected").html(cs_out);
    output.find(".mode").html(data.fields.mode);
    setSignal(data.fields.signal);
    clearAutoNoUpdates();
    update_timeout = setTimeout(autoNoUpdates, options.invalid_timeout);

  }

  function update() {
    jq.get("/homecontroller/internet_connection/status", function (data) {
      processData(data);
    });
  }

  function startInterval() {
    stopInterval();
    update();
    ws_generic.register("internet", processData);
    ge_refresh.register("internet", update);
  }

  function stopInterval() {
    ws_generic.deRegister("internet");
    ge_refresh.deRegister("internet");
  }

  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var refresh_internet, show_pings;
jq(document).ready(function() {
  "use strict";
  refresh_internet = new RefreshInternet({output: ".internet-connection"});
  refresh_internet.startInterval();
  show_pings = new ShowRealtimePing({output: ".internet-connection .ping"});
  show_pings.startInterval();

  jq(".internet-connection").on("click", function() {
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
    jq.each(charts, function() {
      content += "<div class='smokeping-chart'><h4>" + this[0] + "</h4><img src='/smokeping/images/" + this[1] + "?" + timestamp + "'></div>";
    });
    jq("#internet-connection-modal .smokeping-charts").html(content);
    content_switch.switchContent("#internet-connection-modal");
  });

  jq("#internet-connection-modal .close").on("click", function () {
    content_switch.switchContent("#main-content");
  });
});
