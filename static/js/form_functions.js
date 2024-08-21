function limpiarCampos() {
    document.getElementById('marca').value = '';
    document.getElementById('modelo').value = '';
    document.getElementById('color').value = '';
    document.getElementById('existencias').value = '';
    document.getElementById('precio').value = '';
    document.getElementById('talla').selectedIndex = 0;
    document.getElementById('tipo').selectedIndex = 0;

    // Crear un formulario temporal para enviar la solicitud de limpieza
    var form = document.createElement('form');
    form.method = 'post';
    form.action = '/add_product';

    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'limpiar';
    input.value = 'true';

    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}
