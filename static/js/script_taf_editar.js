document.getElementById('data').min = new Date().toISOString().split('T')[0];

function updateCharCounter(fieldId, maxLength) {
    const field = document.getElementById(fieldId);
    const counter = document.getElementById(fieldId + '-counter');
    counter.textContent = field.value.length;

    if (field.value.length >= maxLength * 0.9) {
        counter.style.color = '#f44336';
    } else {
        counter.style.color = '#999';
    }
}

document.getElementById('taskForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const taskId = "{{ tarefa.id }}";
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch(`/home/tarefa/edit/${taskId}`, {
        method: 'PATCH',
        body: data
    });

    if (response.ok) {
        showSuccess('Tarefa atualizada!');
        window.location.reload();
    } else {
        showError('Erro ao atualizar tarefa.');
    }
});


function goBack() {
    window.history.back();
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = '❌ ' + message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    successDiv.textContent = '✓ ' + message;
    successDiv.style.display = 'block';

    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}

function hideMessages() {
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('successMessage').style.display = 'none';
}

document.getElementById('titulo').addEventListener('input', function () {
    if (this.value.length > 0 && this.value.length < 3) {
        this.style.borderColor = '#f44336';
    } else {
        this.style.borderColor = '#e0e0e0';
    }
});

document.getElementById('descricao').addEventListener('input', function () {
    if (this.value.length > 0 && this.value.length < 10) {
        this.style.borderColor = '#f44336';
    } else {
        this.style.borderColor = '#e0e0e0';
    }
});

let formChanged = false;
document.getElementById('taskForm').addEventListener('input', function () {
    formChanged = true;
});

window.addEventListener('beforeunload', function (e) {
    if (formChanged) {
        e.preventDefault();
        e.returnValue = '';
    }
});

document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('taskForm').requestSubmit();
    }

    if (e.key === 'Escape') {
        resetForm();
    }
});