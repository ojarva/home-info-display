var Printer = function () {
  "use strict";
  var update_interval;
  function clearLabels() {
    jq(".printer-labels").children().remove();
  }
  function removeCheck() {
    // TODO: this should not remove all check marks.
    jq(".printer-labels i").removeClass("fa-check");
  }

  function printLabel(id) {
    jq.post("/homecontroller/printer/print_label", {"id": id}, function (data) {
      jq(".printer-labels .print-label-" + id + " i").removeClass("fa-spin fa-spinner").addClass("fa-check");
      setTimeout(removeCheck, 2000);
    });
  }

  function processLabels(data) {
    clearLabels();
    var main_elem = jq(".printer-labels");
    jq.each(data, function() {
      main_elem.append("<div class='center-content stripe-box animate-click action-button print-label-" + this.pk + "' data-id='" + this.pk + "'>" + this.fields.name + " <i class='fa fa-fw'></i></div>");
    });
    // TODO: Bind click events
    main_elem.find("div").on("click", function() {
      content_switch.userAction();
      jq(this).find("i").addClass("fa-spin fa-spinner");
      printLabel(jq(this).data("id"));
    });
  }

  function updateLabels() {
    jq.get("/homecontroller/printer/get_labels", function(data) {
      processLabels(data);
    });
  }



  function fetchStatus() {
    var main = jq("#print-modal .printer-jobs-content");
    main.find("li").remove();
    main.slideUp();
    jq("#print-modal .printer-jobs .spinner").slideDown();
    jq.get("/homecontroller/printer/get_status", function(data) {
      jq("#print-modal .printer-jobs .spinner").slideUp();
      main.slideDown();
      jq.each(data, function (key, value) {
        main.find("ul").append("<li data-id='" + key + "'><i class='fa-li fa fa-times-circle'></i>Luotu " + moment(value["time-at-creation"]).fromNow() + "</i>");
      });
      main.find("li").on("click", function() {
        content_switch.userAction();
        var id = jq(this).data("id");
        jq.post("/homecontroller/printer/cancel_job/" + id, function () {
          fetchStatus();
        });
      });
    });
  }

  function fetchPrinters() {
    var status_main = jq("#print-modal .printer-status");
    status_main.find(".printer-status-content").hide().children().remove();
    status_main.find(".spinner").slideDown();
    jq.get("/homecontroller/printer/get_printers", function(data) {
      status_main.find(".spinner").slideUp();
      status_main.find(".printer-status-content").slideDown();
      jq.each(data, function (key, value) {
        var state = value["printer-state"];
        var states = {3: "odottaa", 4: "tulostaa", 5: "pysäytetty"};
        status_main.find(".printer-status-content").append("<h2>" + key + " (" + states[state] + ")</h2><p>Status: " + value["printer-state-message"] + "</p>");
      });
    });
  }


  function startInterval() {
    stopInterval();
    updateLabels();
    update_interval = setInterval(updateLabels, SLOW_UPDATE);
  }

  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
  }

  ge_refresh.register("printer-labels", updateLabels);
  ws_generic.register("printer-labels", processLabels);


  this.fetchStatus = fetchStatus;
  this.fetchPrinters = fetchPrinters;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var printer;

jq(document).ready(function () {
  "use strict";
  printer = new Printer();
  printer.startInterval();

  jq(".main-button-box .print-labels").on("click", function () {
    content_switch.switchContent("#print-modal");
    printer.fetchStatus();
    printer.fetchPrinters();

  });

  jq("#print-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
