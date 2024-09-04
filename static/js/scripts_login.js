document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');

    // Animación de sacudida para los campos vacíos
    inputs.forEach(input => {
        input.addEventListener('invalid', () => {
            input.classList.add('shake');
            setTimeout(() => input.classList.remove('shake'), 500);
        });
    });
});
