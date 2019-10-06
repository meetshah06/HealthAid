function openCity(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}

// function showTabs(){
//   console.log("here")
//   document.getElementById('that-bar').style.display = 'block';
// }

var i = 0;
var txt = "Suggestions based on Quality, Budget, Time and SO much more!"; /* The text */
var speed = 50; /* The speed/duration of the effect in milliseconds */

function typeWriter() {
  if (i < txt.length) {
    document.getElementById("typingText").innerHTML += txt.charAt(i);
    i++;
    setTimeout(typeWriter, speed);
  }
}