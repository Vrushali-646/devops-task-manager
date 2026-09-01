let tasks = JSON.parse(localStorage.getItem("tasks")) || [];
let taskId = parseInt(localStorage.getItem("taskId")) || 0;

function saveTasks() {
    localStorage.setItem("tasks", JSON.stringify(tasks));
    localStorage.setItem("taskId", taskId.toString());
}

function addTask() {
    const taskInput = document.getElementById("taskInput");
    const statusSelect = document.getElementById("statusSelect");
    const taskTitle = taskInput.value.trim();
    const status = statusSelect.value;

    if (taskTitle === "") {
        alert("Please enter a task title.");
        return;
    }

    const task = {
        id: ++taskId,
        title: taskTitle,
        status: status,
        createdAt: new Date().toLocaleString()
    };

    tasks.push(task);
    saveTasks();
    renderTasks();
    
    taskInput.value = "";
    taskInput.focus();
}

function deleteTask(id) {
    if (confirm("Are you sure you want to delete this task?")) {
        tasks = tasks.filter(task => task.id !== id);
        saveTasks();
        renderTasks();
    }
}

function updateStatus(id) {
    const task = tasks.find(t => t.id === id);
    if (task) {
        const statuses = ["Not Started", "Working", "Completed"];
        const currentIndex = statuses.indexOf(task.status);
        const nextIndex = (currentIndex + 1) % statuses.length;
        task.status = statuses[nextIndex];
        saveTasks();
        renderTasks();
    }
}

function editTask(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;

    const newTitle = prompt("Edit task title:", task.title);
    if (newTitle !== null && newTitle.trim() !== "") {
        task.title = newTitle.trim();
        saveTasks();
        renderTasks();
    }
}

function getStatusClass(status) {
    switch(status) {
        case "Not Started":
            return "status-not-started";
        case "Working":
            return "status-working";
        case "Completed":
            return "status-completed";
        default:
            return "";
    }
}

function updateStats() {
    const total = tasks.length;
    const notStarted = tasks.filter(t => t.status === "Not Started").length;
    const working = tasks.filter(t => t.status === "Working").length;
    const completed = tasks.filter(t => t.status === "Completed").length;

    document.getElementById("totalTasks").textContent = total;
    document.getElementById("notStartedCount").textContent = notStarted;
    document.getElementById("workingCount").textContent = working;
    document.getElementById("completedCount").textContent = completed;
}

function renderTasks() {
    const taskList = document.getElementById("taskList");
    const emptyState = document.getElementById("emptyState");
    
    taskList.innerHTML = "";

    if (tasks.length === 0) {
        emptyState.style.display = "block";
        updateStats();
        return;
    }

    emptyState.style.display = "none";

    tasks.forEach(task => {
        const taskCard = document.createElement("div");
        taskCard.className = `task-card ${getStatusClass(task.status)}`;
        
        taskCard.innerHTML = `
            <div class="task-header">
                <h3 class="task-title">${escapeHtml(task.title)}</h3>
                <span class="task-status">${task.status}</span>
            </div>
            <div class="task-meta">
                <small>Created: ${task.createdAt}</small>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-status" onclick="updateStatus(${task.id})" title="Change status">
                    🔄 Change Status
                </button>
                <button class="btn btn-sm btn-edit" onclick="editTask(${task.id})" title="Edit task">
                    ✏️ Edit
                </button>
                <button class="btn btn-sm btn-delete" onclick="deleteTask(${task.id})" title="Delete task">
                    🗑️ Delete
                </button>
            </div>
        `;
        
        taskList.appendChild(taskCard);
    });

    updateStats();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Allow Enter key to add task
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('taskInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addTask();
        }
    });
    renderTasks();
});

