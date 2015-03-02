var RdioPlayer = function() {
  // Creates rdio player control
  var main_elem = jq("#music-api");

  // From http://www.rdio.com/developers/docs/web-playback/callbacks/ref-playstatechanged
  var play_states = {0: "paused",
                     1: "playing",
                     2: "stopped",
                     3: "buffering",
                     4: "paused"}

  main_elem.bind("ready.rdio", function() {
    jq.post("/homecontroller/music/status/state", {"state": "started"});
    ws_generic.register("rdio-control", receivedCommand);
  });

  main_elem.bind("playStateChanged.rdio", function(playState) {
    var state = play_states[playState];
    jq.post("/homecontroller/music/status/state", {"state": state});
  });

  main_elem.bind("playingTrackChanged.rdio", function(playingTrack) {
    // TODO
  });

  main_elem.bind("positionChanged.rdio", function(position) {
    jq.post("/homecontroller/music/status/position", {"position": position});
  });

  main_elem.rdio('GAlNi78J_____zlyYWs5ZG02N2pkaHlhcWsyOWJtYjkyN2xvY2FsaG9zdEbwl7EHvbylWSWFWYMZwfc=');

  function receivedCommand(message) {
    var data = JSON.parse(message);
    if (data.command) {
      var cmd = data.command;
      if (cmd === "play") {
        if (data.key) {
          main_elem.rdio().play(data.key);
        } else {
          main_elem.rdio().play();
        }
      } else if (cmd === "pause") {
        main_elem.rdio().pause();
      } else if (cmd === "next") {
        main_elem.rdio().next();
      } else if (cmd === "previous") {
        main_elem.rdio().previous();
      } else if (cmd === "stop") {
        main_elem.rdio().stop();
      }
    } else if (data.queue) {
      main_elem.rdio().queue(data.key);
    }
  }


};

var MusicControl = function() {

  function control(command) {
    jq.post("/homecontroller/music/control/" + command, function() {

    });
  }

  function stop() {
    control("stop");
  }

  function play() {
    control("play");
  }

  function pause() {
    control("pause");
  }

  function playNext() {
    control("next");
  }

  function playPrevious() {
    control("previous");
  }

  this.stop = stop;
  this.play = play;
  this.pause = pause;
  this.playNext = playNext;
  this.playPrevious = playPrevious;
};

var music;

jq(document).ready(function() {
  music = new Music();
});
