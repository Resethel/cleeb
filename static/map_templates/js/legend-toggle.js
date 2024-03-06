// Javascript for the legend toogle of the `map_templates` application.

window.onload = function() {
    var legend = document.querySelector(".legend");
    legend.addEventListener("mouseover", function() {
        this.classList.remove("--collapsed");
    });
    legend.addEventListener("mouseout", function() {
        this.classList.add("--collapsed");
    });
}