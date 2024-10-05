function toggleFields() {
    const metodoPago = document.getElementById('pago').value;
    const nuevoPrecioField = document.getElementById('nuevo_precio_field');
    const abonoField = document.getElementById('abono_field');
    const primerAbonoInput = document.getElementById('primer_abono');
    const nuevoPrecioInput = document.getElementById('nuevo_precio');

    if (metodoPago === 'Abonos') {
        nuevoPrecioField.style.display = 'block';
        abonoField.style.display = 'block';
        primerAbonoInput.required = true;  // Hacer obligatorio el primer abono
    } else {
        nuevoPrecioField.style.display = 'none';
        abonoField.style.display = 'none';
        primerAbonoInput.required = false;  // Desactivar la obligatoriedad del abono
        nuevoPrecioInput.value = '';  // Limpiar el valor del campo de nuevo precio
    }
}
