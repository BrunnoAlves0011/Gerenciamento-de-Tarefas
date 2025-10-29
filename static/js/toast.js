function showToast(message, duration = 3000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        console.error("Toast container not found.");
        return;
    }

    const toastElement = document.createElement('div');
    toastElement.classList.add('toast');
    toastElement.textContent = message;

    toastContainer.prepend(toastElement);

    // Animate in
    setTimeout(() => {
        toastElement.classList.add('show');
    }, 10);

    // Animate out and remove after duration
    setTimeout(() => {
        toastElement.classList.remove('show');
        setTimeout(() => {
            toastElement.remove();
        }, 300);
    }, duration);
}
