document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById("cadastrof");
    
    form.addEventListener('submit', function(event) {
        const nome = document.getElementById("name").value.trim();
        const usuario = document.getElementById("usuario").value.trim();
        const senha = document.getElementById("senha").value;
        const conf_senha = document.getElementById("conf_senha").value;

        if (nome === '' || usuario === '') {
            event.preventDefault(); 
            showToast("Erro: Preencha todos os campos.", 5000);
            return false;
        }

        if (senha !== conf_senha) {
            event.preventDefault(); 
            showToast("Erro: Senhas não coincidem.", 5000);
            return false;
        }

        console.log("Validação OK! Enviando para /cadastro...");
        return true;
    });
});