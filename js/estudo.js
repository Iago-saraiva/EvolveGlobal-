// ---------- ELEMENTOS ----------
const menuButtons = document.querySelectorAll(".menu-btn");
const tabContents = document.querySelectorAll(".tab-content");
const pageTitle = document.getElementById("pageTitle");
const resetAllBtn = document.getElementById("resetAllBtn");

// Dashboard
const todayStudyTime = document.getElementById("todayStudyTime");
const completedTasksCount = document.getElementById("completedTasksCount");
const completedGoalsCount = document.getElementById("completedGoalsCount");
const materialsCount = document.getElementById("materialsCount");
const dailyProgressBar = document.getElementById("dailyProgressBar");
const dailyProgressText = document.getElementById("dailyProgressText");
const pendingTasksCount = document.getElementById("pendingTasksCount");
const notesCount = document.getElementById("notesCount");
const pomodoroSessionsCount = document.getElementById("pomodoroSessionsCount");

// Checklist
const taskInput = document.getElementById("taskInput");
const taskSubject = document.getElementById("taskSubject");
const addTaskBtn = document.getElementById("addTaskBtn");
const taskList = document.getElementById("taskList");
const filterSubject = document.getElementById("filterSubject");

// Notes
const notesArea = document.getElementById("notesArea");
const saveNotesBtn = document.getElementById("saveNotesBtn");

// Goals
const goalInput = document.getElementById("goalInput");
const addGoalBtn = document.getElementById("addGoalBtn");
const goalList = document.getElementById("goalList");

// Materials
const materialName = document.getElementById("materialName");
const materialLink = document.getElementById("materialLink");
const addMaterialBtn = document.getElementById("addMaterialBtn");
const materialsList = document.getElementById("materialsList");

// Stats
const totalTasksStat = document.getElementById("totalTasksStat");
const totalGoalsStat = document.getElementById("totalGoalsStat");
const totalSessionsStat = document.getElementById("totalSessionsStat");
const totalMaterialsStat = document.getElementById("totalMaterialsStat");

// Pomodoro
const focusMinutesInput = document.getElementById("focusMinutes");
const breakMinutesInput = document.getElementById("breakMinutes");
const timerDisplay = document.getElementById("timerDisplay");
const startTimerBtn = document.getElementById("startTimerBtn");
const pauseTimerBtn = document.getElementById("pauseTimerBtn");
const resetTimerBtn = document.getElementById("resetTimerBtn");
const timerMode = document.getElementById("timerMode");
const sessionCountEl = document.getElementById("sessionCount");

// ---------- LOCAL STORAGE ----------
let tasks = JSON.parse(localStorage.getItem("studyhub_tasks")) || [];
let goals = JSON.parse(localStorage.getItem("studyhub_goals")) || [];
let materials = JSON.parse(localStorage.getItem("studyhub_materials")) || [];
let notes = localStorage.getItem("studyhub_notes") || "";
let stats = JSON.parse(localStorage.getItem("studyhub_stats")) || {
  studyMinutesToday: 0,
  pomodoroSessions: 0
};

// ---------- VERIFICA SE O USUÁRIO ESTÁ LOGADO ----------
(function checkLogin() {
  const usuarioSalvo = JSON.parse(localStorage.getItem("usuario"));
  const logadoIndex = localStorage.getItem("logado");

  if (logadoIndex !== "true") {
    alert("Você precisa fazer login primeiro!");
    window.location.href = "login.html";
    return false;
  }

  exibirInfoUsuario(usuarioSalvo);

  return true;
})();
// ---------- NAVEGAÇÃO ----------
menuButtons.forEach(button => {
  button.addEventListener("click", () => {
    menuButtons.forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");

    const tab = button.dataset.tab;

    tabContents.forEach(content => {
      content.classList.remove("active");
      if (content.id === tab) content.classList.add("active");
    });

    pageTitle.textContent = button.textContent.replace(/[^\p{L}\p{N}\s]/gu, "").trim();
  });
});

// ---------- CHECKLIST ----------
function saveTasks() {
  localStorage.setItem("studyhub_tasks", JSON.stringify(tasks));
}

function renderTasks() {
  taskList.innerHTML = "";
  const selectedFilter = filterSubject.value;

  const filteredTasks = tasks.filter(task => {
    return selectedFilter === "Todos" || task.subject === selectedFilter;
  });

  filteredTasks.forEach(task => {
    const li = document.createElement("li");
    if (task.completed) li.classList.add("completed");

    li.innerHTML = `
      <div class="item-left">
        <input type="checkbox" ${task.completed ? "checked" : ""} onchange="toggleTask(${task.id})">
        <span>${task.text}</span>
        <span class="badge">${task.subject}</span>
      </div>
      <div class="item-actions">
        <button class="small-btn delete-btn" onclick="deleteTask(${task.id})">Excluir</button>
      </div>
    `;

    taskList.appendChild(li);
  });

  updateDashboard();
  updateStats();
}

function addTask() {
  const text = taskInput.value.trim();
  const subject = taskSubject.value;

  if (!text) {
    alert("Digite uma tarefa.");
    return;
  }

  tasks.push({
    id: Date.now(),
    text,
    subject,
    completed: false
  });

  taskInput.value = "";
  saveTasks();
  renderTasks();
}

function toggleTask(id) {
  tasks = tasks.map(task =>
    task.id === id ? { ...task, completed: !task.completed } : task
  );
  saveTasks();
  renderTasks();
}

function deleteTask(id) {
  tasks = tasks.filter(task => task.id !== id);
  saveTasks();
  renderTasks();
}

window.toggleTask = toggleTask;
window.deleteTask = deleteTask;

addTaskBtn.addEventListener("click", addTask);
filterSubject.addEventListener("change", renderTasks);

// ---------- NOTES ----------
function saveNotes() {
  localStorage.setItem("studyhub_notes", notesArea.value);
  updateDashboard();
  alert("Anotações salvas com sucesso!");
}

saveNotesBtn.addEventListener("click", saveNotes);

// ---------- GOALS ----------
function saveGoals() {
  localStorage.setItem("studyhub_goals", JSON.stringify(goals));
}

function renderGoals() {
  goalList.innerHTML = "";

  goals.forEach(goal => {
    const li = document.createElement("li");
    if (goal.completed) li.classList.add("completed");

    li.innerHTML = `
      <div class="item-left">
        <input type="checkbox" ${goal.completed ? "checked" : ""} onchange="toggleGoal(${goal.id})">
        <span>${goal.text}</span>
      </div>
      <div class="item-actions">
        <button class="small-btn delete-btn" onclick="deleteGoal(${goal.id})">Excluir</button>
      </div>
    `;

    goalList.appendChild(li);
  });

  updateDashboard();
  updateStats();
}

function addGoal() {
  const text = goalInput.value.trim();

  if (!text) {
    alert("Digite uma meta.");
    return;
  }

  goals.push({
    id: Date.now(),
    text,
    completed: false
  });

  goalInput.value = "";
  saveGoals();
  renderGoals();
}

function toggleGoal(id) {
  goals = goals.map(goal =>
    goal.id === id ? { ...goal, completed: !goal.completed } : goal
  );
  saveGoals();
  renderGoals();
}

function deleteGoal(id) {
  goals = goals.filter(goal => goal.id !== id);
  saveGoals();
  renderGoals();
}

window.toggleGoal = toggleGoal;
window.deleteGoal = deleteGoal;

addGoalBtn.addEventListener("click", addGoal);

// ---------- MATERIALS ----------

// Função para definir os materiais padrão (sempre substitui os existentes)
function setDefaultMaterials() {
  // Cria 3 materiais padrão
  const defaultMaterials = [
    {
      id: Date.now(),
      name: "Guia de JavaScript Completo",
      link: "https://developer.mozilla.org/pt-BR/docs/Web/JavaScript"
    },
    {
      id: Date.now() + 1,
      name: "HTML5 - Material de Apoio",
      link: "https://developer.mozilla.org/pt-BR/docs/Web/HTML"
    },
    {
      id: Date.now() + 2,
      name: "CSS3 - Material de apoio",
      link: "https://developer.mozilla.org/pt-BR/docs/Web/CSS"
    }
  ];
  
  materials = defaultMaterials;
  saveMaterials();
}

// Função saveMaterials permanece a mesma
function saveMaterials() {
  localStorage.setItem("studyhub_materials", JSON.stringify(materials));
}

function renderMaterials() {
  materialsList.innerHTML = "";

  materials.forEach(material => {
    const li = document.createElement("li");

    li.innerHTML = `
      <div class="item-left">
        <span><strong>${material.name}</strong></span>
      </div>
      <div class="item-actions">
        <a href="${material.link}" target="_blank">
          <button class="small-btn">Abrir</button>
        </a>
        <button class="small-btn delete-btn" onclick="deleteMaterial(${material.id})">Excluir</button>
      </div>
    `;

    materialsList.appendChild(li);
  });

  updateDashboard();
  updateStats();
}

function addMaterial() {
  const name = materialName.value.trim();
  const link = materialLink.value.trim();

  if (!name || !link) {
    alert("Preencha o nome e o link da apostila.");
    return;
  }

  materials.push({
    id: Date.now(),
    name,
    link
  });

  materialName.value = "";
  materialLink.value = "";

  saveMaterials();
  renderMaterials();
}

function deleteMaterial(id) {
  materials = materials.filter(material => material.id !== id);
  saveMaterials();
  renderMaterials();
}

window.deleteMaterial = deleteMaterial;

setDefaultMaterials();
renderMaterials();

// Adiciona o evento do botão
addMaterialBtn.addEventListener("click", addMaterial);

// ---------- POMODORO ----------
let timer;
let timeLeft = 25 * 60;
let isRunning = false;
let isFocusMode = true;

function updateTimerDisplay() {
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  timerDisplay.textContent =
    `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function startTimer() {
  if (isRunning) return;

  isRunning = true;

  timer = setInterval(() => {
    timeLeft--;
    updateTimerDisplay();

    if (timeLeft <= 0) {
      clearInterval(timer);
      isRunning = false;

      if (isFocusMode) {
        stats.pomodoroSessions++;
        stats.studyMinutesToday += Number(focusMinutesInput.value);
        localStorage.setItem("studyhub_stats", JSON.stringify(stats));

        alert("Sessão de foco concluída! Hora da pausa 😎");
        isFocusMode = false;
        timerMode.textContent = "Pausa";
        timeLeft = Number(breakMinutesInput.value) * 60;
      } else {
        alert("Pausa finalizada! Bora voltar pro foco 🚀");
        isFocusMode = true;
        timerMode.textContent = "Foco";
        timeLeft = Number(focusMinutesInput.value) * 60;
      }

      updateTimerDisplay();
      sessionCountEl.textContent = stats.pomodoroSessions;
      updateDashboard();
      updateStats();
    }
  }, 1000);
}

function pauseTimer() {
  clearInterval(timer);
  isRunning = false;
}

function resetTimer() {
  clearInterval(timer);
  isRunning = false;
  isFocusMode = true;
  timerMode.textContent = "Foco";
  timeLeft = Number(focusMinutesInput.value) * 60;
  updateTimerDisplay();
}

focusMinutesInput.addEventListener("change", () => {
  if (!isRunning && isFocusMode) {
    timeLeft = Number(focusMinutesInput.value) * 60;
    updateTimerDisplay();
  }
});

breakMinutesInput.addEventListener("change", () => {
  if (!isRunning && !isFocusMode) {
    timeLeft = Number(breakMinutesInput.value) * 60;
    updateTimerDisplay();
  }
});

startTimerBtn.addEventListener("click", startTimer);
pauseTimerBtn.addEventListener("click", pauseTimer);
resetTimerBtn.addEventListener("click", resetTimer);

// ---------- DASHBOARD / STATS ----------
function updateDashboard() {
  const completedTasks = tasks.filter(task => task.completed).length;
  const pendingTasks = tasks.filter(task => !task.completed).length;
  const completedGoals = goals.filter(goal => goal.completed).length;
  const notesLength = notesArea.value.trim().length > 0 ? 1 : 0;

  todayStudyTime.textContent = `${stats.studyMinutesToday} min`;
  completedTasksCount.textContent = completedTasks;
  completedGoalsCount.textContent = completedGoals;
  materialsCount.textContent = materials.length;
  pendingTasksCount.textContent = pendingTasks;
  notesCount.textContent = notesLength;
  pomodoroSessionsCount.textContent = stats.pomodoroSessions;
  sessionCountEl.textContent = stats.pomodoroSessions;

  const totalItems = tasks.length + goals.length;
  const doneItems = completedTasks + completedGoals;
  const progress = totalItems > 0 ? Math.round((doneItems / totalItems) * 100) : 0;

  dailyProgressBar.style.width = `${progress}%`;
  dailyProgressText.textContent = `${progress}%`;
}

function updateStats() {
  totalTasksStat.textContent = tasks.length;
  totalGoalsStat.textContent = goals.length;
  totalSessionsStat.textContent = stats.pomodoroSessions;
  totalMaterialsStat.textContent = materials.length;
}

// ---------- RESET GERAL ----------
resetAllBtn.addEventListener("click", () => {
  const confirmReset = confirm("Tem certeza que deseja apagar todos os dados?");
  if (!confirmReset) return;

  localStorage.removeItem("studyhub_tasks");
  localStorage.removeItem("studyhub_goals");
  localStorage.removeItem("studyhub_materials");
  localStorage.removeItem("studyhub_notes");
  localStorage.removeItem("studyhub_stats");

  tasks = [];
  goals = [];
  materials = [];
  notes = "";
  stats = {
    studyMinutesToday: 0,
    pomodoroSessions: 0
  };

  notesArea.value = "";
  renderTasks();
  renderGoals();
  renderMaterials();
  updateDashboard();
  updateStats();
  resetTimer();

  alert("Tudo foi resetado com sucesso.");
});

// ---------- INICIALIZAÇÃO ----------
function init() {
  notesArea.value = notes;
  timeLeft = Number(focusMinutesInput.value) * 60;
  updateTimerDisplay();
  renderTasks();
  renderGoals();
  renderMaterials();
  updateDashboard();
  updateStats();
}

init();