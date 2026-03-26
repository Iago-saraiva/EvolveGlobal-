console.log("Code Studio Ultra carregado 🚀");

// =========================
// ELEMENTOS
// =========================
const projectList = document.getElementById("projectList");
const projectNameDisplay = document.getElementById("projectNameDisplay");

const newProjectBtn = document.getElementById("newProjectBtn");
const renameProjectBtn = document.getElementById("renameProjectBtn");
const deleteProjectBtn = document.getElementById("deleteProjectBtn");

const runBtn = document.getElementById("runBtn");
const copyBtn = document.getElementById("copyBtn");
const clearBtn = document.getElementById("clearBtn");
const resetBtn = document.getElementById("resetBtn");
const refreshPreviewBtn = document.getElementById("refreshPreviewBtn");
const previewFrame = document.getElementById("previewFrame");

const tabs = document.querySelectorAll(".tab");

const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");
const mobileSidebarBtn = document.getElementById("mobileSidebarBtn");
const closeSidebarBtn = document.getElementById("closeSidebarBtn");

// =========================
// STORAGE KEYS
// =========================
const STORAGE_PROJECTS_KEY = "code_studio_ultra_projects";
const STORAGE_CURRENT_PROJECT_KEY = "code_studio_ultra_current_project";

// =========================
// ESTADO
// =========================
let editor = null;
let currentFile = "html";

const defaultFiles = {
  html: `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Meu Projeto</title>
</head>
<body>
  <div class="container">
    <h1>Olá, mundo! 🚀</h1>
    <p>Seu mini VS Code está funcionando.</p>

    <button onclick="mudarTexto()">Clique aqui</button>
    <p id="texto">Texto inicial</p>
  </div>
</body>
</html>`,

  css: `body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #f5f7fb;
}

.container {
  padding: 30px;
}

h1 {
  color: #007acc;
}

button {
  padding: 10px 16px;
  border: none;
  background: #007acc;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}

button:hover {
  background: #005f99;
}`,

  js: `function mudarTexto() {
  document.getElementById("texto").textContent = "Texto alterado com JavaScript! 😎";
}`
};

let projects = loadProjects();
let currentProjectId = loadCurrentProjectId();

// =========================
// HELPERS
// =========================
function generateId() {
  return Date.now().toString() + Math.random().toString(36).slice(2);
}

function cloneDefaultFiles() {
  return {
    html: defaultFiles.html,
    css: defaultFiles.css,
    js: defaultFiles.js
  };
}

function getLanguageFromFile(file) {
  const map = {
    html: "html",
    css: "css",
    js: "javascript"
  };
  return map[file] || "plaintext";
}

function getCurrentProject() {
  return projects.find(project => project.id === currentProjectId) || null;
}

function formatDate(dateString) {
  try {
    const date = new Date(dateString);
    return date.toLocaleString("pt-BR");
  } catch {
    return "Sem data";
  }
}

// =========================
// LOCALSTORAGE
// =========================
function saveProjects() {
  localStorage.setItem(STORAGE_PROJECTS_KEY, JSON.stringify(projects));
  localStorage.setItem(STORAGE_CURRENT_PROJECT_KEY, currentProjectId || "");
}

function loadProjects() {
  const saved = localStorage.getItem(STORAGE_PROJECTS_KEY);

  if (!saved) {
    const firstProject = {
      id: generateId(),
      name: "Meu Projeto 1",
      files: cloneDefaultFiles(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    return [firstProject];
  }

  try {
    const parsed = JSON.parse(saved);

    if (!Array.isArray(parsed) || parsed.length === 0) {
      const firstProject = {
        id: generateId(),
        name: "Meu Projeto 1",
        files: cloneDefaultFiles(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      return [firstProject];
    }

    return parsed.map(project => ({
      id: project.id || generateId(),
      name: project.name || "Projeto sem nome",
      files: {
        html: project.files?.html ?? defaultFiles.html,
        css: project.files?.css ?? defaultFiles.css,
        js: project.files?.js ?? defaultFiles.js
      },
      createdAt: project.createdAt || new Date().toISOString(),
      updatedAt: project.updatedAt || new Date().toISOString()
    }));
  } catch (error) {
    console.error("Erro ao carregar projetos:", error);
    const firstProject = {
      id: generateId(),
      name: "Meu Projeto 1",
      files: cloneDefaultFiles(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    return [firstProject];
  }
}

function loadCurrentProjectId() {
  const saved = localStorage.getItem(STORAGE_CURRENT_PROJECT_KEY);

  if (saved && projects.find(project => project.id === saved)) {
    return saved;
  }

  return projects[0]?.id || null;
}

// =========================
// SIDEBAR MOBILE
// =========================
function openSidebar() {
  sidebar.classList.add("open");
  sidebarOverlay.classList.add("show");
}

function closeSidebar() {
  sidebar.classList.remove("open");
  sidebarOverlay.classList.remove("show");
}

mobileSidebarBtn.addEventListener("click", openSidebar);
closeSidebarBtn.addEventListener("click", closeSidebar);
sidebarOverlay.addEventListener("click", closeSidebar);

// =========================
// RENDERIZAÇÃO
// =========================
function renderProjectList() {
  projectList.innerHTML = "";

  projects.forEach(project => {
    const button = document.createElement("button");
    button.className = "project-item";
    if (project.id === currentProjectId) {
      button.classList.add("active");
    }

    button.innerHTML = `
      <span class="project-item-name">${escapeHtml(project.name)}</span>
      <span class="project-item-meta">Atualizado: ${formatDate(project.updatedAt)}</span>
    `;

    button.addEventListener("click", () => {
      switchProject(project.id);
      if (window.innerWidth <= 768) {
        closeSidebar();
      }
    });

    projectList.appendChild(button);
  });
}

function renderCurrentProjectInfo() {
  const currentProject = getCurrentProject();

  if (!currentProject) {
    projectNameDisplay.textContent = "Nenhum projeto";
    return;
  }

  projectNameDisplay.textContent = currentProject.name;
}

function updateActiveTabs() {
  tabs.forEach(tab => {
    tab.classList.toggle("active", tab.dataset.file === currentFile);
  });
}

// =========================
// SEGURANÇA BÁSICA PARA innerHTML
// =========================
function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// =========================
// PROJETOS
// =========================
function createNewProject() {
  const projectName = prompt("Digite o nome do novo projeto:", `Meu Projeto ${projects.length + 1}`);

  if (!projectName || !projectName.trim()) return;

  const newProject = {
    id: generateId(),
    name: projectName.trim(),
    files: cloneDefaultFiles(),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  projects.unshift(newProject);
  currentProjectId = newProject.id;
  currentFile = "html";

  saveProjects();
  renderProjectList();
  renderCurrentProjectInfo();
  loadCurrentProjectIntoEditor();
  updatePreview();
}

function renameCurrentProject() {
  const currentProject = getCurrentProject();
  if (!currentProject) return;

  const newName = prompt("Digite o novo nome do projeto:", currentProject.name);

  if (!newName || !newName.trim()) return;

  currentProject.name = newName.trim();
  currentProject.updatedAt = new Date().toISOString();

  saveProjects();
  renderProjectList();
  renderCurrentProjectInfo();
}

function deleteCurrentProject() {
  const currentProject = getCurrentProject();
  if (!currentProject) return;

  const confirmDelete = confirm(`Deseja excluir o projeto "${currentProject.name}"?`);
  if (!confirmDelete) return;

  projects = projects.filter(project => project.id !== currentProject.id);

  if (projects.length === 0) {
    const fallbackProject = {
      id: generateId(),
      name: "Meu Projeto 1",
      files: cloneDefaultFiles(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    projects.push(fallbackProject);
  }

  currentProjectId = projects[0].id;
  currentFile = "html";

  saveProjects();
  renderProjectList();
  renderCurrentProjectInfo();
  loadCurrentProjectIntoEditor();
  updatePreview();
}

function switchProject(projectId) {
  if (projectId === currentProjectId) return;

  saveCurrentEditorContent();

  currentProjectId = projectId;
  currentFile = "html";

  saveProjects();
  renderProjectList();
  renderCurrentProjectInfo();
  loadCurrentProjectIntoEditor();
  updatePreview();
}

// =========================
// EDITOR / ARQUIVOS
// =========================
function loadCurrentProjectIntoEditor() {
  const currentProject = getCurrentProject();
  if (!currentProject || !editor) return;

  const content = currentProject.files[currentFile] ?? "";
  editor.setValue(content);
  monaco.editor.setModelLanguage(editor.getModel(), getLanguageFromFile(currentFile));
  updateActiveTabs();
}

function saveCurrentEditorContent() {
  const currentProject = getCurrentProject();
  if (!currentProject || !editor) return;

  currentProject.files[currentFile] = editor.getValue();
  currentProject.updatedAt = new Date().toISOString();

  saveProjects();
  renderProjectList();
  renderCurrentProjectInfo();
}

function switchFile(file) {
  if (!editor || file === currentFile) return;

  saveCurrentEditorContent();
  currentFile = file;
  loadCurrentProjectIntoEditor();
}

function clearCurrentTab() {
  const currentProject = getCurrentProject();
  if (!currentProject || !editor) return;

  const fileNames = {
    html: "index.html",
    css: "style.css",
    js: "script.js"
  };

  const confirmClear = confirm(`Deseja limpar o arquivo ${fileNames[currentFile]}?`);
  if (!confirmClear) return;

  currentProject.files[currentFile] = "";
  currentProject.updatedAt = new Date().toISOString();

  editor.setValue("");
  saveProjects();
  renderProjectList();
  renderCurrentProjectInfo();
  updatePreview();
}

function resetCurrentProject() {
  const currentProject = getCurrentProject();
  if (!currentProject || !editor) return;

  const confirmReset = confirm("Deseja restaurar o projeto para o código padrão?");
  if (!confirmReset) return;

  currentProject.files = cloneDefaultFiles();
  currentProject.updatedAt = new Date().toISOString();
  currentFile = "html";

  saveProjects();
  renderProjectList();
  renderCurrentProjectInfo();
  loadCurrentProjectIntoEditor();
  updatePreview();
}

// =========================
// PREVIEW
// =========================
function buildPreviewDocument() {
  const currentProject = getCurrentProject();
  if (!currentProject) return "<h1>Sem projeto</h1>";

  const html = currentProject.files.html || "";
  const css = currentProject.files.css || "";
  const js = currentProject.files.js || "";

  let finalHtml = html;

  if (finalHtml.includes("</head>")) {
    finalHtml = finalHtml.replace(
      "</head>",
      `<style>${css}</style></head>`
    );
  } else {
    finalHtml = `<style>${css}</style>\n${finalHtml}`;
  }

  if (finalHtml.includes("</body>")) {
    finalHtml = finalHtml.replace(
      "</body>",
      `<script>${js}<\/script></body>`
    );
  } else {
    finalHtml += `\n<script>${js}<\/script>`;
  }

  return finalHtml;
}

function updatePreview() {
  saveCurrentEditorContent();
  previewFrame.srcdoc = buildPreviewDocument();
}

// =========================
// COPIAR
// =========================
async function copyCurrentTab() {
  if (!editor) return;

  try {
    await navigator.clipboard.writeText(editor.getValue());

    const original = copyBtn.textContent;
    copyBtn.textContent = "✅ Copiado!";

    setTimeout(() => {
      copyBtn.textContent = original;
    }, 1200);
  } catch (error) {
    console.error("Erro ao copiar:", error);
    alert("Não foi possível copiar o código.");
  }
}

// =========================
// MONACO
// =========================
require.config({
  paths: {
    vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs"
  }
});

require(["vs/editor/editor.main"], function () {
  editor = monaco.editor.create(document.getElementById("editor"), {
    value: getCurrentProject()?.files?.[currentFile] ?? "",
    language: getLanguageFromFile(currentFile),
    theme: "vs-dark",
    automaticLayout: true,
    fontSize: 15,
    fontFamily: "Consolas, 'Courier New', monospace",
    minimap: { enabled: true },
    roundedSelection: true,
    scrollBeyondLastLine: false,
    wordWrap: "on",
    tabSize: 2
  });

  editor.onDidChangeModelContent(() => {
    const currentProject = getCurrentProject();
    if (!currentProject) return;

    currentProject.files[currentFile] = editor.getValue();
    currentProject.updatedAt = new Date().toISOString();

    saveProjects();
    renderProjectList();
    renderCurrentProjectInfo();
  });

  renderProjectList();
  renderCurrentProjectInfo();
  updateActiveTabs();
  updatePreview();
});

// =========================
// EVENTOS
// =========================
tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    switchFile(tab.dataset.file);
  });
});

newProjectBtn.addEventListener("click", createNewProject);
renameProjectBtn.addEventListener("click", renameCurrentProject);
deleteProjectBtn.addEventListener("click", deleteCurrentProject);

runBtn.addEventListener("click", () => {
  updatePreview();

  const original = runBtn.textContent;
  runBtn.textContent = "✅ Executado!";

  setTimeout(() => {
    runBtn.textContent = original;
  }, 1200);
});

refreshPreviewBtn.addEventListener("click", updatePreview);
copyBtn.addEventListener("click", copyCurrentTab);
clearBtn.addEventListener("click", clearCurrentTab);
resetBtn.addEventListener("click", resetCurrentProject);

// =========================
// ATALHOS
// =========================
window.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
    e.preventDefault();

    saveCurrentEditorContent();
    updatePreview();

    const original = runBtn.textContent;
    runBtn.textContent = "💾 Salvo!";

    setTimeout(() => {
      runBtn.textContent = original;
    }, 1200);
  }
});

// =========================
// INICIALIZAÇÃO EXTRA
// =========================
renderProjectList();
renderCurrentProjectInfo();
updateActiveTabs();