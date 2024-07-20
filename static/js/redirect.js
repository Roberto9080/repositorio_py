document.addEventListener('DOMContentLoaded', function() {
    const messageElement = document.querySelector('.message.success');
    if (messageElement) {
        setTimeout(function() {
            window.location.href = redirectUrl;
        }, 1000); // 2000 milisegundos = 2 segundos
    }
});
