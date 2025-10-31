// // Salvar informações pessoais
// document.getElementById('profileForm').addEventListener('submit', async function (e) {
//     e.preventDefault();

//     const formData = {
//         email: document.getElementById('email').value,
//         fullname: document.getElementById('fullname').value
//     };

//     try {
//         const response = await fetch('/perfil/atualizar', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(formData)
//         });

//         if (response.ok) {
//             showSuccess('Informações atualizadas com sucesso!');
//         } else {
//             showError('Erro ao atualizar informações. Tente novamente.');
//         }
//     } catch (error) {
//         console.error('Erro:', error);
//         showError('Erro de conexão. Verifique sua internet.');
//     }
// });

// // Alterar senha
// document.getElementById('passwordForm').addEventListener('submit', async function (e) {
//     e.preventDefault();

//     const currentPassword = document.getElementById('currentPassword').value;
//     const newPassword = document.getElementById('newPassword').value;
//     const confirmPassword = document.getElementById('confirmPassword').value;

//     if (newPassword !== confirmPassword) {
//         showError('As senhas não coincidem!');
//         return;
//     }

//     if (newPassword.length < 6) {
//         showError('A senha deve ter pelo menos 6 caracteres!');
//         return;
//     }

//     try {
//         const response = await fetch('/perfil/alterar-senha', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({
//                 current_password: currentPassword,
//                 new_password: newPassword
//             })
//         });

//         if (response.ok) {
//             showSuccess('Senha alterada com sucesso!');
//             document.getElementById('passwordForm').reset();
//         } else {
//             const data = await response.json();
//             showError(data.message || 'Erro ao alterar senha. Verifique a senha atual.');
//         }
//     } catch (error) {
//         console.error('Erro:', error);
//         showError('Erro de conexão. Verifique sua internet.');
//     }
// });

// function resetForm() {
//     document.getElementById('profileForm').reset();
//     location.reload();
// }

// function confirmDeleteAccount() {
//     const confirm1 = confirm('⚠️ ATENÇÃO: Você tem certeza que deseja excluir sua conta?');
//     if (confirm1) {
//         const confirm2 = confirm('Esta ação é IRREVERSÍVEL! Todos os seus dados serão perdidos. Deseja continuar?');
//         if (confirm2) {
//             deleteAccount();
//         }
//     }
// }

// async function deleteAccount() {
//     try {
//         const response = await fetch('/perfil/excluir-conta', {
//             method: 'DELETE'
//         });

//         if (response.ok) {
//             alert('Conta excluída com sucesso. Você será redirecionado.');
//             window.location.href = '/';
//         } else {
//             showError('Erro ao excluir conta. Tente novamente.');
//         }
//     } catch (error) {
//         console.error('Erro:', error);
//         showError('Erro de conexão. Verifique sua internet.');
//     }
// }

// function showSuccess(message) {
//     const successDiv = document.getElementById('successMessage');
//     successDiv.textContent = '✓ ' + message;
//     successDiv.style.display = 'block';

//     setTimeout(() => {
//         successDiv.style.display = 'none';
//     }, 5000);

//     hideError();
// }

// function showError(message) {
//     const errorDiv = document.getElementById('errorMessage');
//     errorDiv.textContent = '❌ ' + message;
//     errorDiv.style.display = 'block';

//     setTimeout(() => {
//         errorDiv.style.display = 'none';
//     }, 5000);

//     hideSuccess();
// }

// function hideSuccess() {
//     document.getElementById('successMessage').style.display = 'none';
// }

// function hideError() {
//     document.getElementById('errorMessage').style.display = 'none';
// }