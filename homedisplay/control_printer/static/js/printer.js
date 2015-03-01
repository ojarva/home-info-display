var Printer = function () {
  var update_interval;
  function clearLabels() {
    $(".printer-labels").children().remove();
  }

  function processLabels(data) {
    clearLabels();
    var main_elem = $(".printer-labels");
    $.each(data, function() {
      main_elem.append("<div class='center-content stripe-box animate-click action-button print-label-"+this.pk+"' data-id='"+this.pk+"'>"+this.fields.name+" <i class='fa fa-fw'></i></div>");
    });
    // TODO: Bind click events
    main_elem.find("div").on("click", function() {
      $(this).find("i").addClass("fa-spin fa-spinner");
      printLabel($(this).data("id"));
    });
  }

  function updateLabels() {
    $.get("/homecontroller/printer/get_labels", function(data) {
      processLabels(data);
    });
  }

  function removeCheck() {
    // TODO: this should not remove all check marks.
    $(".printer-labels i").removeClass("fa-check");
  }

  function printLabel(id) {
    $.post("/homecontroller/printer/print_label", {"id": id}, function (data) {
      $(".printer-labels .print-label-"+id+" i").removeClass("fa-spin fa-spinner").addClass("fa-check");
      setTimeout(removeCheck, 2000);
    });
  }

  function fetchStatus() {
    var main = $("#print-modal .printer-jobs-content");
    main.find("li").remove();
    main.slideUp();
    $("#print-modal .printer-jobs .spinner").slideDown();
    $.get("/homecontroller/printer/get_status", function(data) {
      $("#print-modal .printer-jobs .spinner").slideUp();
      main.slideDown();
      $.each(data, function (key, value) {
        main.find("ul").append("<li data-id='"+key+"'><i class='fa-li fa fa-times-circle'></i>Luotu "+moment(value["time-at-creation"]).fromNow()+"</i>");
      });
      main.find("li").on("click", function() {
        var id = $(this).data("id");
        $.post("/homecontroller/printer/cancel_job/"+id, function () {
          fetchStatus();
        });
      });
    });
  }

  function fetchPrinters() {
    var status_main = $("#print-modal .printer-status");
    status_main.find(".printer-status-content").hide().children().remove();
    status_main.find(".spinner").slideDown();
    $.get("/homecontroller/printer/get_printers", function(data) {
      status_main.find(".spinner").slideUp();
      status_main.find(".printer-status-content").slideDown();
      $.each(data, function (key, value) {
        state = value["printer-state"];
        states = {3: "odottaa", 4: "tulostaa", 5: "pysäytetty"};
        status_main.find(".printer-status-content").append("<h2>"+key+" ("+states[state]+")</h2><p>Status: "+value["printer-state-message"]+"</p>");
      });
    });
  }


  function startInterval() {
    stopInterval();
    updateLabels();
    update_interval = setInterval(updateLabels, 60 * 60 * 1000);
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

$(document).ready(function () {
  printer = new Printer();
  printer.startInterval();

  $(".main-button-box .print-labels").on("click", function () {
    switchVisibleContent("#print-modal");
    printer.fetchStatus();
    printer.fetchPrinters();

  });

  $("#print-modal .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
