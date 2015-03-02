moment.locale("fi");

var ContentSwitch = function () {
  "use strict";
  var switch_visible_content_timeout,
      switch_visible_content_currently_active = "#main-content";

  function mainContent() {
    jq(switch_visible_content_currently_active).find(".close").trigger("click");
    if (switch_visible_content_timeout) {
      switch_visible_content_timeout = clearTimeout(switch_visible_content_timeout);
    }
  }

  function resetSwitchToMain() {
    if (switch_visible_content_timeout) {
      switch_visible_content_timeout = clearTimeout(switch_visible_content_timeout);
    }
    switch_visible_content_timeout = setTimeout(mainContent, 60 * 1000);
  }

  function switchContent(elem) {
    if (switch_visible_content_timeout) {
      switch_visible_content_timeout = clearTimeout(switch_visible_content_timeout);
    }
    jq(".content-box").hide(); // Hide all content boxes
    jq("html, body").animate({ scrollTop: 0 }, "fast"); // Always scroll to top.
    jq("#navbar").collapse("hide"); // Hide menu, if visible
    if (elem !== "#main-content") {
      switch_visible_content_currently_active = elem;
      switch_visible_content_timeout = setTimeout(mainContent, 60 * 1000);
      jq(elem).show();
    }
  }

  function userAction() {
    if (switch_visible_content_currently_active != "#main-content") {
      resetSwitchToMain();
    }
  }

  this.switchContent = switchContent;
  this.mainContent = mainContent;
  this.userAction = userAction;
};

var content_switch;

jq(document).ready(function() {
  "use strict";
  content_switch = new ContentSwitch();
  jq(".animate-click").each(function () {
    jq(this).data("original-bg-color", jq(this).css("background-color"));
  });
  jq(".animate-click").on("click", function () {
    jq(this).stop(true).css("background-color", jq(this).data("original-bg-color")).effect("highlight", {color: "#ffffff"}, 500);
  });

});

var VERY_SLOW_UPDATE = 12 * 60 * 60 * 1000; // Update twice per day
var SLOW_UPDATE = 60 * 60 * 1000; // once per hour
var FAST_UPDATE = 10 * 60 * 1000; // once per 10 minutes
