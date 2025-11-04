function showAlert(message, type = 'info') {
    const alert = document.getElementById('alert');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.display = 'block';

    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

async function exportarDados() {
    try {
        showLoading(true);
        const response = await fetch('/config/exportar');

        if (!response.ok) {
            throw new Error('Erro ao exportar dados');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backup_tarefas_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showAlert('✅ Backup exportado com sucesso!', 'success');
    } catch (error) {
        showAlert('❌ Erro ao exportar dados: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function importarDeURL() {
    const url = document.getElementById('urlImport').value.trim();

    if (!url) {
        showAlert('⚠️ Por favor, insira uma URL válida', 'error');
        return;
    }

    try {
        showLoading(true);
        const response = await fetch('/config/importar-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert(`✅ ${data.mensagem}`, 'success');
            document.getElementById('urlImport').value = '';

            // Recarrega a página após 2 segundos
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showAlert(`❌ ${data.error || 'Erro ao importar dados'}`, 'error');
        }
    } catch (error) {
        showAlert('❌ Erro ao importar dados: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function importarDeArquivo(input) {
    const file = input.files[0];

    if (!file) return;

    try {
        showLoading(true);
        const formData = new FormData();
        formData.append('arquivo', file);

        const response = await fetch('/config/importar-arquivo', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert(`✅ ${data.mensagem}`, 'success');
            input.value = '';

            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showAlert(`❌ ${data.error || 'Erro ao importar dados'}`, 'error');
        }
    } catch (error) {
        showAlert('❌ Erro ao importar arquivo: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}