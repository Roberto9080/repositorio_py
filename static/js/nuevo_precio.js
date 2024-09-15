function toggleNuevoPrecio() {
    var metodoPago = document.getElementById('pago').value;
    var nuevoPrecioField = document.getElementById('nuevo_precio_field');
    if (metodoPago === 'Abonos') {
        nuevoPrecioField.style.display = 'block';
    } else {
        nuevoPrecioField.style.display = 'none';
    }
}