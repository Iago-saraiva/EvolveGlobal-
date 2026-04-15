// =========================
// ELEMENTOS
// =========================
const codeEditor = document.getElementById("codeEditor");
const preview = document.getElementById("preview");

const newProjectBtn = document.getElementById("newProjectBtn");
const renameProjectBtn = document.getElementById("renameProjectBtn");
const deleteProjectBtn = document.getElementById("deleteProjectBtn");

const prevProjectBtn = document.getElementById("prevProjectBtn");
const nextProjectBtn = document.getElementById("nextProjectBtn");
const projectSelector = document.getElementById("projectSelector");
const currentProjectBadge = document.getElementById("currentProjectBadge");

const createFolderBtn = document.getElementById("createFolderBtn");
const createFileBtn = document.getElementById("createFileBtn");
const fileTree = document.getElementById("fileTree");

const currentFileName = document.getElementById("currentFileName");
const currentFileMeta = document.getElementById("currentFileMeta");
const renameFileBtn = document.getElementById("renameFileBtn");
const deleteFileBtn = document.getElementById("deleteFileBtn");

const runBtn = document.getElementById("runBtn");
const refreshPreviewBtn = document.getElementById("refreshPreviewBtn");
const openMainFilesBtn = document.getElementById("openMainFilesBtn");
const copyBtn = document.getElementById("copyBtn");
const clearBtn = document.getElementById("clearBtn");
const resetBtn = document.getElementById("resetBtn");

// TERMINAL
const openTerminalBtn = document.getElementById("openTerminalBtn");
const terminalPanel = document.getElementById("terminalPanel");
const terminalOutput = document.getElementById("terminalOutput");
const terminalTitle = document.getElementById("terminalTitle");
const runPythonBtn = document.getElementById("runPythonBtn");
const clearTerminalBtn = document.getElementById("clearTerminalBtn");
const closeTerminalBtn = document.getElementById("closeTerminalBtn");

// =========================
// VARIÁVEIS GLOBAIS
// =========================
let currentProjectName = localStorage.getItem("currentProjectName") || "Meu Projeto";
let currentFilePath = "index.html";

// =========================
// LOGIN
// =========================
function verificarLogin() {
  const usuarioSalvo = JSON.parse(localStorage.getItem("usuario"));
  const logadoIndex = localStorage.getItem("logado");

  if (logadoIndex !== "true" || !usuarioSalvo) {
    mostrarMensagemLogin();
    return false;
  }

  exibirInfoUsuario(usuarioSalvo);
  return true;
}

function mostrarMensagemLogin() {
  if (document.querySelector(".login-overlay")) return;

  const overlay = document.createElement("div");
  overlay.className = "login-overlay";
  overlay.innerHTML = `
        <div class="login-message">
          <p>Você precisa estar logado para acessar esta página.</p>
          <button onclick="redirecionarLogin()">Fazer Login</button>
        </div>
      `;
  document.body.appendChild(overlay);

  const appContainer = document.querySelector(".app-container");
  if (appContainer) {
    appContainer.style.opacity = "0.5";
    appContainer.style.pointerEvents = "none";
  }

  const bottomActions = document.querySelector(".bottom-actions");
  if (bottomActions) {
    bottomActions.style.opacity = "0.5";
    bottomActions.style.pointerEvents = "none";
  }
}

window.redirecionarLogin = function () {
  localStorage.setItem("redirectAfterLogin", window.location.pathname);
  window.location.href = "login.html";
};

function exibirInfoUsuario(usuario) {
  const userInfoDiv = document.getElementById("user-info");
  if (!userInfoDiv) return;

  const nomeUsuario = usuario.nome || usuario.email || "Usuário";

  userInfoDiv.innerHTML = `
        <span>👤 Olá, <strong>${nomeUsuario}</strong>!</span>
        <button onclick="fazerLogout()">Sair</button>
      `;
  userInfoDiv.classList.remove("hidden");
}

window.fazerLogout = function () {
  if (confirm("Deseja realmente sair? Seus dados serão salvos.")) {
    localStorage.removeItem("usuario");
    localStorage.removeItem("logado");
    window.location.href = "login.html";
  }
};

if (!verificarLogin()) {
  throw new Error("Usuário não autenticado");
}

// =========================
// USER INFO MODAL
// =========================
        // Dados do usuário (você pode modificar ou buscar de uma API)
    // Dados do usuário
    const userData = {
      name: "Ana Silva Santos",
      email: "ana.silva@email.com",
      phone: "(11) 98765-4321",
      image: "https://randomuser.me/api/portraits/women/1.jpg"
    };

    // Função para abrir o modal
    function abrirModal() {
      // Preenche os dados do usuário
      document.getElementById('userNameDisplay').textContent = userData.name;
      document.getElementById('userEmailDisplay').textContent = userData.email;
      document.getElementById('userPhoneDisplay').textContent = userData.phone;
      document.getElementById('userImageDisplay').src = userData.image;
      
      // Mostra o modal e o overlay
      const modal = document.getElementById('userModal');
      const overlay = document.getElementById('modalOverlay');
      
      modal.classList.add('show');
      overlay.classList.add('show');
      
      // Previne scroll do body
      document.body.style.overflow = 'hidden';
    }

    // Função para fechar o modal
    function fecharModal() {
      const modal = document.getElementById('userModal');
      const overlay = document.getElementById('modalOverlay');
      
      modal.classList.remove('show');
      overlay.classList.remove('show');
      
      // Restaura o scroll do body
      document.body.style.overflow = '';
    }

    // Configurar eventos quando o DOM estiver carregado
    document.addEventListener('DOMContentLoaded', function() {
      // Botão para abrir o modal
      const openModalBtn = document.getElementById('openUserModalBtn');
      if (openModalBtn) {
        openModalBtn.addEventListener('click', abrirModal);
      }
      
      // Botão para fechar o modal
      const closeModalBtn = document.getElementById('closeModalBtn');
      if (closeModalBtn) {
        closeModalBtn.addEventListener('click', fecharModal);
      }
      
      // Fechar ao clicar no overlay
      const overlay = document.getElementById('modalOverlay');
      if (overlay) {
        overlay.addEventListener('click', fecharModal);
      }
      
      // Fechar modal com a tecla ESC
      document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
          const modal = document.getElementById('userModal');
          if (modal.classList.contains('show')) {
            fecharModal();
          }
        }
      });
    });

    // Função opcional para atualizar dados do usuário dinamicamente
    function atualizarDadosUsuario(novoUsuario) {
      userData.name = novoUsuario.name;
      userData.email = novoUsuario.email;
      userData.phone = novoUsuario.phone;
      userData.image = novoUsuario.image;
    }

    // Aqui você pode adicionar o resto do código do seu editor.js
    console.log('Sistema de modal carregado com sucesso!');
// =========================
// DADOS DO PROJETO
// =========================
function getDefaultProjectData() {
  return {
    folders: [],
    files: {
      "index.html": "<h1>Olá, mundo!</h1>\n<p>Seu projeto está on</p>",
      "style.css": "body {\n  font-family: Arial, sans-serif;\n  text-align: center;\n  padding: 40px;\n  background: #f1f5f9;\n}\n\nh1 {\n  color: #0ea5e9;\n}",
      "script.js": "console.log('Projeto carregado com sucesso!');"
    }
  };
}

function getAllProjects() {
  const projects = [];

  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key.startsWith("project_")) {
      projects.push(key.replace("project_", ""));
    }
  }

  if (projects.length === 0) {
    projects.push("Meu Projeto");
  }

  return [...new Set(projects)].sort();
}

function getCurrentProjectData() {
  const saved = localStorage.getItem("project_" + currentProjectName);

  if (!saved) {
    return getDefaultProjectData();
  }

  try {
    const parsed = JSON.parse(saved);

    if (parsed.html !== undefined || parsed.css !== undefined || parsed.js !== undefined) {
      return {
        folders: [],
        files: {
          "index.html": parsed.html || "",
          "style.css": parsed.css || "",
          "script.js": parsed.js || ""
        }
      };
    }

    if (!parsed.files) parsed.files = {};
    if (!parsed.folders) parsed.folders = [];

    return parsed;
  } catch (error) {
    return getDefaultProjectData();
  }
}

function saveCurrentProjectData(projectData) {
  localStorage.setItem("project_" + currentProjectName, JSON.stringify(projectData));
  localStorage.setItem("currentProjectName", currentProjectName);
}

function ensureCurrentProjectExists() {
  const key = "project_" + currentProjectName;
  if (!localStorage.getItem(key)) {
    saveCurrentProjectData(getDefaultProjectData());
  }
}

// =========================
// HELPERS
// =========================
function isSupportedFile(filePath) {
  return filePath.endsWith(".html") || filePath.endsWith(".css") || filePath.endsWith(".js");
}

function isPythonFile(filePath) {
  return filePath && filePath.endsWith(".py");
}

function getFileType(filePath) {
  if (filePath.endsWith(".html")) return "HTML";
  if (filePath.endsWith(".css")) return "CSS";
  if (filePath.endsWith(".js")) return "JavaScript";
  if (filePath.endsWith(".py")) return "Python";
  return "Texto";
}

function normalizePath(path) {
  return path.replace(/\/+/g, "/").replace(/^\/|\/$/g, "");
}

function fileExists(projectData, path) {
  return Object.prototype.hasOwnProperty.call(projectData.files, path);
}

function folderExists(projectData, folderName) {
  return projectData.folders.includes(folderName);
}

// =========================
// TERMINAL PYTHON
// =========================
function appendTerminalLine(text, className = "") {
  const line = document.createElement("div");
  line.className = "terminal-line " + className;
  line.textContent = text;
  terminalOutput.appendChild(line);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function openPythonTerminal() {
  if (!isPythonFile(currentFilePath)) {
    alert("Abra um arquivo .py para usar o terminal Python.");
    return;
  }

  terminalPanel.classList.add("active");
  terminalTitle.textContent = "Terminal Python • " + currentFilePath;

  if (terminalOutput.innerHTML.trim() === "") {
    appendTerminalLine("Python Terminal iniciado para: " + currentFilePath, "terminal-info");
    appendTerminalLine("Clique em 'Rodar Python' para simular a execução do arquivo.", "terminal-info");
  }
}

function closePythonTerminal() {
  terminalPanel.classList.remove("active");
}

function clearTerminal() {
  terminalOutput.innerHTML = "";
}

function runPythonFile() {
  if (!isPythonFile(currentFilePath)) {
    alert("O terminal Python só funciona com arquivos .py");
    return;
  }

  saveCurrentFileContent();
  terminalPanel.classList.add("active");
  terminalTitle.textContent = "Terminal Python • " + currentFilePath;

  const code = codeEditor.value;
  appendTerminalLine(">>> Executando " + currentFilePath + "...", "terminal-info");

  // Simulação básica de saída de Python
  const lines = code.split("\n");
  let foundPrint = false;
  let syntaxError = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (!line) continue;

    // Detecta print("...")
    const printMatch = line.match(/^print\s*\((.*)\)\s*$/);
    if (printMatch) {
      foundPrint = true;
      let output = printMatch[1].trim();

      // remove aspas simples ou duplas
      if (
        (output.startsWith('"') && output.endsWith('"')) ||
        (output.startsWith("'") && output.endsWith("'"))
      ) {
        output = output.slice(1, -1);
      }

      appendTerminalLine(output, "terminal-success");
      continue;
    }

    // detecta input
    if (line.includes("input(")) {
      appendTerminalLine("[input()] Execução simulada: input não é suportado no navegador.", "terminal-error");
      continue;
    }

    // erro simples: print sem fechar
    if (line.startsWith("print(") && !line.endsWith(")")) {
      syntaxError = true;
      appendTerminalLine("SyntaxError: ')' was never closed", "terminal-error");
      break;
    }
  }

  if (!foundPrint && !syntaxError) {
    appendTerminalLine("Programa executado (simulação).", "terminal-success");
    appendTerminalLine("Dica: use print('Olá') para ver saídas no terminal.", "terminal-info");
  }

  appendTerminalLine(">>> Finalizado.\n", "terminal-info");
}

// =========================
// UI DE PROJETO
// =========================
function updateProjectSelector() {
  const projects = getAllProjects();
  projectSelector.innerHTML = "";

  projects.forEach(project => {
    const option = document.createElement("option");
    option.value = project;
    option.textContent = project;
    if (project === currentProjectName) option.selected = true;
    projectSelector.appendChild(option);
  });

  currentProjectBadge.textContent = "Projeto: " + currentProjectName;
}

function switchProject(projectName) {
  saveCurrentFileContent();

  currentProjectName = projectName;
  localStorage.setItem("currentProjectName", currentProjectName);

  ensureCurrentProjectExists();
  loadProject();
}

function goToPreviousProject() {
  const projects = getAllProjects();
  const currentIndex = projects.indexOf(currentProjectName);
  const prevIndex = currentIndex <= 0 ? projects.length - 1 : currentIndex - 1;
  switchProject(projects[prevIndex]);
}

function goToNextProject() {
  const projects = getAllProjects();
  const currentIndex = projects.indexOf(currentProjectName);
  const nextIndex = currentIndex >= projects.length - 1 ? 0 : currentIndex + 1;
  switchProject(projects[nextIndex]);
}

// =========================
// EXPLORADOR DE ARQUIVOS
// =========================
function renderFileTree() {
  const projectData = getCurrentProjectData();
  fileTree.innerHTML = "";

  const rootFiles = Object.keys(projectData.files).filter(file => !file.includes("/")).sort();
  const folders = [...projectData.folders].sort();

  folders.forEach(folder => {
    const folderWrapper = document.createElement("div");
    folderWrapper.className = "tree-item tree-folder";

    const folderRow = document.createElement("div");
    folderRow.className = "tree-row";

    const folderLabel = document.createElement("div");
    folderLabel.className = "tree-label";
    folderLabel.textContent = "📁 " + folder;

    const folderActions = document.createElement("div");
    folderActions.className = "tree-actions";

    const addFileBtn = document.createElement("button");
    addFileBtn.className = "mini-btn";
    addFileBtn.textContent = "+ Arquivo";
    addFileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      createFile(folder);
    });

    const deleteFolderBtn = document.createElement("button");
    deleteFolderBtn.className = "mini-btn mini-danger";
    deleteFolderBtn.textContent = "Excluir";
    deleteFolderBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteFolder(folder);
    });

    folderActions.appendChild(addFileBtn);
    folderActions.appendChild(deleteFolderBtn);

    folderRow.appendChild(folderLabel);
    folderRow.appendChild(folderActions);

    folderWrapper.appendChild(folderRow);

    const folderFilesContainer = document.createElement("div");
    folderFilesContainer.className = "folder-files";

    const folderFiles = Object.keys(projectData.files)
      .filter(file => file.startsWith(folder + "/"))
      .sort();

    folderFiles.forEach(filePath => {
      const fileWrapper = document.createElement("div");
      fileWrapper.className = "tree-item tree-file" + (currentFilePath === filePath ? " active" : "");

      const fileRow = document.createElement("div");
      fileRow.className = "tree-row";

      const fileLabel = document.createElement("div");
      fileLabel.className = "tree-label";
      fileLabel.textContent = "📄 " + filePath.split("/").pop();
      fileLabel.addEventListener("click", () => openFile(filePath));

      const fileActions = document.createElement("div");
      fileActions.className = "tree-actions";

      const renameBtn = document.createElement("button");
      renameBtn.className = "mini-btn mini-warning";
      renameBtn.textContent = "Renomear";
      renameBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        renameFile(filePath);
      });

      const deleteBtn = document.createElement("button");
      deleteBtn.className = "mini-btn mini-danger";
      deleteBtn.textContent = "Excluir";
      deleteBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteFile(filePath);
      });

      fileActions.appendChild(renameBtn);
      fileActions.appendChild(deleteBtn);

      fileRow.appendChild(fileLabel);
      fileRow.appendChild(fileActions);
      fileWrapper.appendChild(fileRow);
      folderFilesContainer.appendChild(fileWrapper);
    });

    folderWrapper.appendChild(folderFilesContainer);
    fileTree.appendChild(folderWrapper);
  });

  rootFiles.forEach(filePath => {
    const fileWrapper = document.createElement("div");
    fileWrapper.className = "tree-item tree-file" + (currentFilePath === filePath ? " active" : "");

    const fileRow = document.createElement("div");
    fileRow.className = "tree-row";

    const fileLabel = document.createElement("div");
    fileLabel.className = "tree-label";
    fileLabel.textContent = "📄 " + filePath;
    fileLabel.addEventListener("click", () => openFile(filePath));

    const fileActions = document.createElement("div");
    fileActions.className = "tree-actions";

    const renameBtn = document.createElement("button");
    renameBtn.className = "mini-btn mini-warning";
    renameBtn.textContent = "Renomear";
    renameBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      renameFile(filePath);
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "mini-btn mini-danger";
    deleteBtn.textContent = "Excluir";
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteFile(filePath);
    });

    fileActions.appendChild(renameBtn);
    fileActions.appendChild(deleteBtn);

    fileRow.appendChild(fileLabel);
    fileRow.appendChild(fileActions);
    fileWrapper.appendChild(fileRow);

    fileTree.appendChild(fileWrapper);
  });

  updateEditorHeader();
}

// =========================
// EDITOR
// =========================
function updateEditorHeader() {
  currentFileName.textContent = currentFilePath || "Nenhum arquivo";
  currentFileMeta.textContent = "Tipo: " + getFileType(currentFilePath);
}

function openFile(filePath) {
  saveCurrentFileContent();

  const projectData = getCurrentProjectData();

  if (!fileExists(projectData, filePath)) {
    alert("Arquivo não encontrado.");
    return;
  }

  currentFilePath = filePath;
  codeEditor.value = projectData.files[filePath];
  updateEditorHeader();
  renderFileTree();
}

function saveCurrentFileContent() {
  if (!currentFilePath) return;

  const projectData = getCurrentProjectData();

  if (!fileExists(projectData, currentFilePath)) return;

  projectData.files[currentFilePath] = codeEditor.value;
  saveCurrentProjectData(projectData);
}

function openMainFiles() {
  openFile("index.html");
}

// =========================
// CRUD DE PASTAS
// =========================
function createFolder() {
  const folderName = prompt("Digite o nome da nova pasta:");

  if (!folderName || folderName.trim() === "") {
    alert("Nome de pasta inválido.");
    return;
  }

  const cleanFolder = normalizePath(folderName.trim());
  const projectData = getCurrentProjectData();

  if (folderExists(projectData, cleanFolder)) {
    alert("Essa pasta já existe.");
    return;
  }

  projectData.folders.push(cleanFolder);
  saveCurrentProjectData(projectData);
  renderFileTree();

  alert("Pasta criada com sucesso!");
}

function deleteFolder(folderName) {
  const projectData = getCurrentProjectData();

  const folderFiles = Object.keys(projectData.files).filter(file => file.startsWith(folderName + "/"));

  if (folderFiles.length > 0) {
    alert("Não é possível excluir uma pasta que contém arquivos.");
    return;
  }

  const confirmDelete = confirm("Deseja excluir a pasta '" + folderName + "'?");

  if (!confirmDelete) return;

  projectData.folders = projectData.folders.filter(folder => folder !== folderName);
  saveCurrentProjectData(projectData);
  renderFileTree();

  alert("Pasta excluída com sucesso!");
}

// =========================
// CRUD DE ARQUIVOS
// =========================
function createFile(preselectedFolder = "") {
  const fileName = prompt("Digite o nome do arquivo (ex: app.js, pagina.html, style2.css, main.py):");

  if (!fileName || fileName.trim() === "") {
    alert("Nome de arquivo inválido.");
    return;
  }

  const cleanFile = fileName.trim();

  if (!cleanFile.includes(".")) {
    alert("O arquivo precisa ter extensão (.html, .css, .js, .py).");
    return;
  }

  const projectData = getCurrentProjectData();
  let targetPath = cleanFile;

  if (preselectedFolder) {
    targetPath = normalizePath(preselectedFolder + "/" + cleanFile);
  } else if (projectData.folders.length > 0) {
    const folderChoice = prompt(
      "Digite o nome da pasta para salvar o arquivo (deixe vazio para raiz):\n\n" +
      projectData.folders.join(", ")
    );

    if (folderChoice && folderChoice.trim() !== "") {
      const chosenFolder = normalizePath(folderChoice.trim());

      if (!folderExists(projectData, chosenFolder)) {
        alert("Pasta não existe.");
        return;
      }

      targetPath = normalizePath(chosenFolder + "/" + cleanFile);
    }
  }

  if (fileExists(projectData, targetPath)) {
    alert("Esse arquivo já existe.");
    return;
  }

  let defaultContent = "";

  if (cleanFile.endsWith(".html")) {
    defaultContent = "<h1>Novo arquivo HTML</h1>";
  } else if (cleanFile.endsWith(".css")) {
    defaultContent = "/* Novo arquivo CSS */";
  } else if (cleanFile.endsWith(".js")) {
    defaultContent = "console.log('Novo arquivo JS');";
  } else if (cleanFile.endsWith(".py")) {
    defaultContent = "print('Olá, Python!')";
  } else {
    defaultContent = "";
  }

  projectData.files[targetPath] = defaultContent;
  saveCurrentProjectData(projectData);

  currentFilePath = targetPath;
  codeEditor.value = defaultContent;

  renderFileTree();
  updateEditorHeader();

  alert("Arquivo criado com sucesso!");
}

function renameFile(filePath = currentFilePath) {
  const projectData = getCurrentProjectData();

  if (!fileExists(projectData, filePath)) {
    alert("Arquivo não encontrado.");
    return;
  }

  const parts = filePath.split("/");
  const oldFileName = parts.pop();
  const folderPath = parts.join("/");

  const newFileName = prompt("Digite o novo nome do arquivo:", oldFileName);

  if (!newFileName || newFileName.trim() === "") {
    alert("Nome inválido.");
    return;
  }

  const cleanNewFileName = newFileName.trim();
  const newPath = folderPath ? normalizePath(folderPath + "/" + cleanNewFileName) : cleanNewFileName;

  if (newPath === filePath) {
    return;
  }

  if (fileExists(projectData, newPath)) {
    alert("Já existe um arquivo com esse nome.");
    return;
  }

  const content = projectData.files[filePath];
  delete projectData.files[filePath];
  projectData.files[newPath] = content;

  if (currentFilePath === filePath) {
    currentFilePath = newPath;
  }

  saveCurrentProjectData(projectData);

  if (currentFilePath === newPath) {
    codeEditor.value = content;
  }

  renderFileTree();
  updateEditorHeader();
  updatePreview();

  alert("Arquivo renomeado com sucesso!");
}

function deleteFile(filePath = currentFilePath) {
  const projectData = getCurrentProjectData();

  if (!fileExists(projectData, filePath)) {
    alert("Arquivo não encontrado.");
    return;
  }

  const protectedFiles = ["index.html", "style.css", "script.js"];
  if (protectedFiles.includes(filePath)) {
    const confirmProtected = confirm(
      "Esse é um arquivo principal do preview (" + filePath + "). Deseja realmente excluir?"
    );

    if (!confirmProtected) return;
  } else {
    const confirmDelete = confirm("Deseja excluir o arquivo '" + filePath + "'?");
    if (!confirmDelete) return;
  }

  delete projectData.files[filePath];

  if (!projectData.files["index.html"]) projectData.files["index.html"] = "";
  if (!projectData.files["style.css"]) projectData.files["style.css"] = "";
  if (!projectData.files["script.js"]) projectData.files["script.js"] = "";

  saveCurrentProjectData(projectData);

  currentFilePath = "index.html";
  codeEditor.value = projectData.files["index.html"] || "";

  renderFileTree();
  updateEditorHeader();
  updatePreview();

  alert("Arquivo excluído com sucesso.");
}

// =========================
// PREVIEW
// =========================
function updatePreview() {
  saveCurrentFileContent();

  const projectData = getCurrentProjectData();

  const html = projectData.files["index.html"] || "";
  const css = "<style>" + (projectData.files["style.css"] || "") + "</style>";
  const js = "<script>" + (projectData.files["script.js"] || "") + "<\/script>";

  preview.srcdoc = html + css + js;
}

// =========================
// PROJETOS
// =========================
function createNewProject() {
  const projectName = prompt("Digite o nome do novo projeto:");

  if (!projectName || projectName.trim() === "") {
    alert("Nome do projeto inválido.");
    return;
  }

  currentProjectName = projectName.trim();
  saveCurrentProjectData(getDefaultProjectData());

  currentFilePath = "index.html";
  loadProject();

  alert("Projeto criado com sucesso: " + currentProjectName);
}

function renameCurrentProject() {
  const newName = prompt("Digite o novo nome do projeto:", currentProjectName);

  if (!newName || newName.trim() === "") {
    alert("Nome inválido.");
    return;
  }

  const cleanName = newName.trim();

  if (cleanName === currentProjectName) return;

  const existing = localStorage.getItem("project_" + cleanName);
  if (existing) {
    alert("Já existe um projeto com esse nome.");
    return;
  }

  const oldData = localStorage.getItem("project_" + currentProjectName);

  if (oldData) {
    localStorage.setItem("project_" + cleanName, oldData);
    localStorage.removeItem("project_" + currentProjectName);
  }

  currentProjectName = cleanName;
  localStorage.setItem("currentProjectName", currentProjectName);

  updateProjectSelector();

  alert("Projeto renomeado com sucesso!");
}

function deleteCurrentProject() {
  const confirmDelete = confirm("Tem certeza que deseja excluir o projeto '" + currentProjectName + "'?");

  if (!confirmDelete) return;

  localStorage.removeItem("project_" + currentProjectName);

  const projects = getAllProjects().filter(project => project !== currentProjectName);

  if (projects.length === 0) {
    currentProjectName = "Meu Projeto";
    saveCurrentProjectData(getDefaultProjectData());
  } else {
    currentProjectName = projects[0];
    ensureCurrentProjectExists();
  }

  currentFilePath = "index.html";
  loadProject();

  alert("Projeto excluído com sucesso!");
}

function resetCurrentProject() {
  const confirmReset = confirm("Deseja resetar todo o projeto?");

  if (!confirmReset) return;

  saveCurrentProjectData(getDefaultProjectData());
  currentFilePath = "index.html";
  loadProject();

  alert("Projeto resetado com sucesso.");
}

// =========================
// AÇÕES GERAIS
// =========================
function copyCurrentFile() {
  navigator.clipboard.writeText(codeEditor.value)
    .then(() => {
      alert("Código copiado com sucesso!");
    })
    .catch(() => {
      alert("Erro ao copiar o código.");
    });
}

function clearCurrentFile() {
  const confirmClear = confirm("Deseja limpar o conteúdo do arquivo atual?");

  if (!confirmClear) return;

  codeEditor.value = "";
  saveCurrentFileContent();
  updatePreview();
}

function loadProject() {
  ensureCurrentProjectExists();

  const projectData = getCurrentProjectData();

  if (!fileExists(projectData, currentFilePath)) {
    currentFilePath = "index.html";
  }

  if (!fileExists(projectData, currentFilePath)) {
    currentFilePath = Object.keys(projectData.files)[0] || "index.html";
  }

  codeEditor.value = projectData.files[currentFilePath] || "";

  updateProjectSelector();
  updateEditorHeader();
  renderFileTree();
  updatePreview();
}

// =========================
// EVENTOS
// =========================
newProjectBtn.addEventListener("click", createNewProject);
renameProjectBtn.addEventListener("click", renameCurrentProject);
deleteProjectBtn.addEventListener("click", deleteCurrentProject);

prevProjectBtn.addEventListener("click", goToPreviousProject);
nextProjectBtn.addEventListener("click", goToNextProject);
projectSelector.addEventListener("change", (e) => switchProject(e.target.value));

createFolderBtn.addEventListener("click", createFolder);
createFileBtn.addEventListener("click", () => createFile());

renameFileBtn.addEventListener("click", () => renameFile());
deleteFileBtn.addEventListener("click", () => deleteFile());

runBtn.addEventListener("click", () => {
  if (isPythonFile(currentFilePath)) {
    openPythonTerminal();
    runPythonFile();

    const originalText = runBtn.textContent;
    runBtn.textContent = "🐍 Python Rodado!";

    setTimeout(() => {
      runBtn.textContent = originalText;
    }, 1200);

    return;
  }

  updatePreview();

  const originalText = runBtn.textContent;
  runBtn.textContent = "✅ Executado!";

  setTimeout(() => {
    runBtn.textContent = originalText;
  }, 1200);
});

refreshPreviewBtn.addEventListener("click", updatePreview);
openMainFilesBtn.addEventListener("click", openMainFiles);

copyBtn.addEventListener("click", copyCurrentFile);
clearBtn.addEventListener("click", clearCurrentFile);
resetBtn.addEventListener("click", resetCurrentProject);

codeEditor.addEventListener("input", saveCurrentFileContent);

// TERMINAL EVENTOS
openTerminalBtn.addEventListener("click", openPythonTerminal);
runPythonBtn.addEventListener("click", runPythonFile);
clearTerminalBtn.addEventListener("click", clearTerminal);
closeTerminalBtn.addEventListener("click", closePythonTerminal);

// =========================
// INICIALIZAÇÃO
// =========================
loadProject();