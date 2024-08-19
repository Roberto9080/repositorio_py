// static/js/form_functions.js

function limpiarCampos() {
    document.getElementById('marca').value = '';
    document.getElementById('modelo').value = '';
    document.getElementById('color').value = '';
    document.getElementById('existencias').value = '';
    document.getElementById('precio').value = '';
    document.getElementById('talla').selectedIndex = 0;
    document.getElementById('tipo').selectedIndex = 0;
}
