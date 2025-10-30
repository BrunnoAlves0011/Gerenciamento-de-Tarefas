let currentFilter = 'all';

function goBack() {
    window.location.href = '/home';
}

function createTask() {
    window.location.href = '/home/adicionar_tarefa';
}

// function filterTasks(filter) {
//     currentFilter = filter;

//     // Atualizar botões ativos
//     document.querySelectorAll('.filter-btn').forEach(btn => {
//         btn.classList.remove('active');
//     });
//     event.target.classList.add('active');

//     applyFilters();
// }

// function applyFilters() {
//     const searchTerm = document.getElementById('searchInput').value.toLowerCase();
//     const priority = document.getElementById('priorityFilter').value;
//     const category = document.getElementById('categoryFilter').value;
//     const tasks = document.querySelectorAll('.task-card');

//     tasks.forEach(task => {
//         const status = task.dataset.status;
//         const taskPriority = task.dataset.priority;
//         const taskCategory = task.dataset.category;
//         const title = task.querySelector('.task-title').textContent.toLowerCase();
//         const description = task.querySelector('.task-description').textContent.toLowerCase();

//         let show = true;

//         // Filtro de status
//         if (currentFilter !== 'all') {
//             if (currentFilter === 'completed' && status !== 'completed') show = false;
//             if (currentFilter === 'pending' && status !== 'pending') show = false;
//         }

//         // Filtro de prioridade
//         if (priority && taskPriority !== priority) show = false;

//         // Filtro de categoria
//         if (category && taskCategory !== category) show = false;

//         // Filtro de busca
//         if (searchTerm && !title.includes(searchTerm) && !description.includes(searchTerm)) {
//             show = false;
//         }

//         task.style.display = show ? 'block' : 'none';
//     });

//     checkEmptyState();
// }

// function searchTasks() {
//     applyFilters();
// }

function checkEmptyState() {
    const visibleTasks = document.querySelectorAll('.task-card[style="display: block;"], .task-card:not([style*="display: none"])');
    const container = document.getElementById('tasksContainer');

    if (visibleTasks.length === 0) {
        if (!document.querySelector('.empty-state')) {
            container.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📭</div>
                            <div class="empty-state-title">Nenhuma tarefa encontrada</div>
                            <div class="empty-state-text">Tente ajustar os filtros ou criar uma nova tarefa</div>
                        </div>
                    `;
        }
    }
}

async function completeTask(button) {
    const taskCard = button.closest('.task-card');
    const taskId = taskCard.dataset.taskId;

    if (taskCard.classList.contains('completed')) {
        taskCard.classList.remove('completed');
        taskCard.dataset.status = 'pending';
        button.style.display = 'flex';
    } else {
        if (confirm('Marcar esta tarefa como concluída?')) {
            taskCard.classList.add('completed');
            taskCard.dataset.status = 'completed';
            button.style.display = 'none';
            try {
                const response = await fetch(`/home/tarefa/finish/${taskId}`, {
                    method: 'PATCH'
                });

                if (response.ok) {
                    console.log('Tarefa Concluida com sucesso!');
                    taskCard.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        taskCard.style.transform = 'scale(1)';
                    }, 200);
                } else {
                    console.error('Erro ao excluir tarefa:', response.status);
                    alert('Erro ao concluir tarefa. Tente novamente.');
                }
            } catch (error) {
                console.error('Erro na requisição:', error);
                alert('Erro de conexão. Verifique sua internet.');
            }
        }
    }
}

function editTask(button) {
    alert('Abrindo formulário para editar tarefa...');
}

async function deleteTask(button) {
    if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        const taskCard = button.closest('.task-card');
        const taskId = taskCard.dataset.taskId;

        if (!taskId) {
            alert('ID da tarefa não encontrado!');
            return;
        }

        try {
            const response = await fetch(`/home/tarefa/del/${taskId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log('Tarefa excluída com sucesso!');
                taskCard.style.opacity = '0';
                taskCard.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    taskCard.remove();
                    checkEmptyState();
                }, 300);
            } else {
                console.error('Erro ao excluir tarefa:', response.status);
                alert('Erro ao excluir tarefa. Tente novamente.');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            alert('Erro de conexão. Verifique sua internet.');
        }
    }
}

// Atalhos de teclado
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + K para focar na busca
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }

    // Ctrl/Cmd + N para nova tarefa
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createTask();
    }
});