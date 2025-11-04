let currentFilter = 'all';

function goBack() {
    window.location.href = '/home';
}

function createTask() {
    window.location.href = '/home/adicionar_tarefa';
}

function viewTask(event) {
    const taskCard = event.currentTarget.closest('.task-card');
    const taskId = taskCard.dataset.taskId;
    
    window.location.href = `/home/tarefa_visualizar/${taskId}`;
}

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
    event.stopPropagation();

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
    const taskCard = button.closest('.task-card');
    const taskId = taskCard.dataset.taskId;
    event.stopPropagation();

    window.location.href = `/home/edit/${taskId}`;
}

async function deleteTask(button) {
    event.stopPropagation();
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

document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }

    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createTask();
    }
});