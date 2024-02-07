/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function datasets_search() {
  var elements = document.getElementsByClassName("search-result__item__categories__more");
  for(var i = 0; i < elements.length; i++)
  {
    elements[i].classList.toggle("--show");
  }
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.closest('.search-result__item__categories__more__button'))
  {
    var dropdowns = document.getElementsByClassName("search-result__item__categories__more");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('--show')) {
        openDropdown.classList.remove('--show');
      }
    }
  }
}