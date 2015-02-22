$(document).ready(function () {
  // These are wall display specific hacks to prevent issues with not-too-well functioning touchscreen.
  // This file should not be included in any other UI.

  // Disabling right click menu is evil. However, Ubuntu&Chrome&touchscreen means problems when context menu is triggered.
  $("body").bind("contextmenu", function () {
    return false;
  });

  // Clear text selection. It's easy to accidentally select text, and rather difficult to de-select.
  setInterval(function () {
    window.getSelection().empty();
  }, 1000);
});
