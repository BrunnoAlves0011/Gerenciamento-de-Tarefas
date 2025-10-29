// Adicionar event listener quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById("cadastrof");
    
    form.addEventListener('submit', function(event) {
        const nome = document.getElementById("name").value.trim();
        const usuario = document.getElementById("usuario").value.trim();
        const senha = document.getElementById("senha").value;
        const conf_senha = document.getElementById("conf_senha").value;

        // Validação dos campos vazios
        if (nome === '' || usuario === '') {
            event.preventDefault(); // Impede o envio
            showToast("Erro: Preencha todos os campos.", 5000);
            return false;
        }

        // Validação das senhas
        if (senha !== conf_senha) {
            event.preventDefault(); // Impede o envio
            showToast("Erro: Senhas não coincidem.", 5000);
            return false;
        }

        // Se passou nas validações, deixa o form ser enviado normalmente
        console.log("Validação OK! Enviando para /cadastro...");
        return true;
    });
});