var Printer = function () {
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

  this.fetchStatus = fetchStatus;
  this.fetchPrinters = fetchPrinters;
};

var printer;

$(document).ready(function () {
  printer = new Printer();

  $(".main-button-box .print-labels").on("click", function () {
    switchVisibleContent("#print-modal");
    printer.fetchStatus();
    printer.fetchPrinters();

  });

  $("#print-modal .close").on("click", function() {
    switchVisibleContent("#main-content");
  });
});
