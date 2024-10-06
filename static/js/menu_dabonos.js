function toggleMenu(id) {
    var menu = document.getElementById(id);
    menu.classList.toggle('show');
    // Si es un historial de abonos, también cambiamos el estilo de 'display'
    if (menu.classList.contains('show')) {
        menu.style.display = 'table-row';
    } else {
        menu.style.display = 'none';
    }
}

window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName('dropdown-content');
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
};
