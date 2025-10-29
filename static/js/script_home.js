async function logout() {
    try {
        const response = await fetch('/logout', {
            method: 'GET'
        });

        if (response.ok) {
            console.log('Logout realizado com sucesso!');
            window.location.reload();
        } else {
            console.error('Erro ao fazer logout:', response.status);
            alert('Erro ao fazer logout. Tente novamente.');
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        alert('Erro de conexão. Verifique sua internet.');
    }
}