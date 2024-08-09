// toggle_visibility.js

document.addEventListener('DOMContentLoaded', (event) => {
    // Inicialmente ocultar los productos
    document.querySelector('.table-container').style.display = 'none';
});

function toggleVisibility() {
    const tableContainer = document.querySelector('.table-container');
    const visibilityIcon = document.getElementById('visibilityIcon');

    if (tableContainer.style.display === 'none') {
        tableContainer.style.display = 'block';
        visibilityIcon.classList.remove('fa-eye-slash'); // Ojo cerrado
        visibilityIcon.classList.add('fa-eye'); // Ojo abierto
    } else {
        tableContainer.style.display = 'none';
        visibilityIcon.classList.remove('fa-eye'); // Ojo abierto
        visibilityIcon.classList.add('fa-eye-slash'); // Ojo cerrado
    }
}
