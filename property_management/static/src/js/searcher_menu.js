function search_buttons() {
    document.getElementById("property_search_down").onclick = function () { search_button_down() };
    document.getElementById("property_search_up").onclick = function () { search_button_up() };
}

function search_button_down() {
    var accordion = document.getElementById('property_accordion_navbar')
    accordion.style.maxHeight= '22em';
    document.getElementById("property_search_button_down").style.display = 'none';
    document.getElementById("property_search_button_up").style.display = 'flex';
    document.getElementById("property_search_down").style.display="none";
    document.getElementById("property_search_up").style.display="flex";

}

function search_button_up() {
    var accordion = document.getElementById('property_accordion_navbar')
    accordion.style.maxHeight = '0em';
    document.getElementById("property_search_button_up").style.display = 'none'
    document.getElementById("property_search_button_down").style.display = 'flex';
    document.getElementById("property_search_up").style.display="none";
    document.getElementById("property_search_down").style.display="flex"
}

window.addEventListener("load", search_buttons);






