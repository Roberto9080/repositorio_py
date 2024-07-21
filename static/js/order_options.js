function showOrderOptions() {
    var orderOptions = document.getElementById('order-options');
    if (orderOptions.style.display === 'none' || orderOptions.style.display === '') {
        orderOptions.style.display = 'block';
    } else {
        orderOptions.style.display = 'none';
    }
}
