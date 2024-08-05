document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const confirmMessage = document.createElement('div');
    confirmMessage.classList.add('confirm-message');
    confirmMessage.innerHTML = `
        <p>¿Estás seguro de que quieres realizar la venta?</p>
        <button id="confirm-yes" class="btn-confirm">Sí</button>
        <button id="confirm-no" class="btn-cancel">No</button>
    `;
    document.body.appendChild(confirmMessage);
    
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        confirmMessage.style.display = 'block';
    });

    document.getElementById('confirm-yes').addEventListener('click', function () {
        form.submit();
    });

    document.getElementById('confirm-no').addEventListener('click', function () {
        confirmMessage.style.display = 'none';
    });
});
