function resetForm() {
    document.getElementById('profileForm').reset();
    location.reload();
}

function confirmDeleteAccount() {
    const confirm1 = confirm('⚠️ ATENÇÃO: Você tem certeza que deseja excluir sua conta?');
    if (confirm1) {
        const confirm2 = confirm('Esta ação é IRREVERSÍVEL! Todos os seus dados serão perdidos. Deseja continuar?');
        if (confirm2) {
            deleteAccount();
        }
    }
}

async function deleteAccount() {
    try {
        const response = await fetch(`/perfil/excluir-conta/${USER_ID}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('Conta excluída com sucesso. Você será redirecionado.');
            window.location.href = '/login';
        } else {
            showError('Erro ao excluir conta. Tente novamente.');
        }
    } catch (error) {
        console.error('Erro:', error);
        showError('Erro de conexão. Verifique sua internet.');
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    successDiv.textContent = '✓ ' + message;
    successDiv.style.display = 'block';

    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 5000);

    hideError();
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = '❌ ' + message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);

    hideSuccess();
}

function hideSuccess() {
    document.getElementById('successMessage').style.display = 'none';
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}