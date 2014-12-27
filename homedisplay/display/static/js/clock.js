function handleClock() {
    var days = new Array("su", "ma", "ti", "ke", "to", "pe", "la");
    var currentTime = new Date ( );
    var currentDay = days[currentTime.getDay()];
    var currentDate = currentTime.getDate();
    var currentMonth = currentTime.getMonth()+1;
    $("#calendar").html(currentDay+" "+currentDate+"."+currentMonth+".");
    var currentTime = new Date ( );
    var currentHours = currentTime.getHours ( );
    var currentMinutes = currentTime.getMinutes ( );
    var currentSeconds = currentTime.getSeconds ( );
    currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
    currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;
    $("#clock").html(currentHours+":"+currentMinutes+":"+currentSeconds);
}$(document).ready(function() {    handleClock();    setInterval("handleClock()", 1000); // 1s});