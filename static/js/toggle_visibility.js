document.addEventListener('DOMContentLoaded', (event) => {
    // Inicialmente ocultar los productos y el mensaje de resultados encontrados
    document.querySelector('.table-container').style.display = 'none';
    document.querySelector('.results-message').style.display = 'none';
});

function toggleVisibility() {
    const tableContainer = document.querySelector('.table-container');
    const resultsMessage = document.querySelector('.results-message');
    const visibilityIcon = document.getElementById('visibilityIcon');

    if (tableContainer.style.display === 'none') {
        // Mostrar la tabla de productos y el mensaje de resultados encontrados
        tableContainer.style.display = 'block';
        resultsMessage.style.display = 'block';
        visibilityIcon.classList.remove('fa-eye-slash'); // Ojo cerrado
        visibilityIcon.classList.add('fa-eye'); // Ojo abierto
    } else {
        // Ocultar la tabla de productos y el mensaje de resultados encontrados
        tableContainer.style.display = 'none';
        resultsMessage.style.display = 'none';
        visibilityIcon.classList.remove('fa-eye'); // Ojo abierto
        visibilityIcon.classList.add('fa-eye-slash'); // Ojo cerrado
    }
}
