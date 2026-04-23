// ==================== CONFIGURAÇÃO ====================
const API_URL = 'http://localhost:5000/api';

// ==================== ELEMENTOS ====================
const codeEditor = document.getElementById('codeEditor');
const preview = document.getElementById('preview');
const fileTree = document.getElementById('fileTree');

// ==================== ESTADO ====================
let currentProjectId = null;
let currentProjectName = 'Meu Projeto';
let currentFilePath = 'index.html';
let projetos = [];
let arquivos = {};
let pastas = [];
let saveTimeout = null;

// ==================== API ====================
async function req(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', 'Authorization': token };
    const res = await fetch(API_URL + endpoint, { ...options, headers });

    if (res.status === 401) {
        window.location.href = 'login.html';
        throw new Error('Não autorizado');
    }
    return res;
}

// ==================== LOGIN ====================
async function checkLogin() {
    const token = localStorage.getItem('token');
    if (!token) return window.location.href = 'login.html';

    const res = await fetch(API_URL + '/verificar-token', {
        headers: { 'Authorization': token }
    });

    if (!res.ok) return window.location.href = 'login.html';

    const user = JSON.parse(localStorage.getItem('user') || '{}');

    const userInfoDiv = document.getElementById('user-info');
    if (userInfoDiv) {
        userInfoDiv.innerHTML = '👤 Olá, ' + user.nome + '! <button onclick="logout()">Sair</button>';  
        userInfoDiv.classList.remove('hidden');
    }

    const userNameSpan = document.getElementById('userNameDisplay');
    const userEmailP = document.getElementById('userEmailDisplay');
    const userImage = document.getElementById('userImageDisplay');
    if (userNameSpan) userNameSpan.innerText = user.nome;
    if (userEmailP) userEmailP.innerText = user.email;
    if (userImage) userImage.src = 'https://ui-avatars.com/api/?background=007acc&color=fff&name=' + encodeURIComponent(user.nome);

    await loadProjects();
}

window.logout = () => {
    localStorage.clear();
    window.location.href = 'login.html';
};

// ==================== PROJETOS ====================
async function loadProjects() {
    try {
        const res = await req('/studio/projetos');
        projetos = await res.json();

        if (projetos.length === 0) {
            await createProject('Meu Projeto');
            return loadProjects();
        }

        currentProjectId = projetos[0].id;
        currentProjectName = projetos[0].nome;
        
        updateProjectSelector();
        await loadFiles();
    } catch(e) {
        console.error('Erro ao carregar projetos:', e);
    }
}

async function createProject(nome) {
    const res = await req('/studio/projetos', { method: 'POST', body: JSON.stringify({ nome }) });
    const data = await res.json();
    
    if (data.success) {
        const defaults = {
            'index.html': '<h1>Olá, mundo!</h1><p>Bem-vindo ao Evolve Code Studio!</p>',
            'style.css': 'body { font-family: Arial; text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; min-height: 100vh; } h1 { font-size: 2.5rem; }',
            'script.js': 'console.log("Projeto carregado com sucesso!");'
        };
        
        for (const [path, content] of Object.entries(defaults)) {
            await req('/studio/projetos/' + data.id + '/arquivos', {
                method: 'POST',
                body: JSON.stringify({ caminho: path, conteudo: content })
            });
        }
    }
}

function updateProjectSelector() {
    const selector = document.getElementById('projectSelector');
    if (!selector) return;
    
    selector.innerHTML = '';
    projetos.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.textContent = p.nome;
        if (p.id === currentProjectId) option.selected = true;
        selector.appendChild(option);
    });
    
    const badge = document.getElementById('currentProjectBadge');
    if (badge) badge.textContent = 'Projeto: ' + currentProjectName;
}

async function switchProject(projectId) {
    const project = projetos.find(p => p.id == projectId);
    if (!project) return;
    
    currentProjectId = project.id;
    currentProjectName = project.nome;
    await loadFiles();
    updateProjectSelector();
}

// ==================== ARQUIVOS ====================
async function loadFiles() {
    try {
        const res = await req(`/studio/projetos/${currentProjectId}/arquivos`);
        const files = await res.json();

        arquivos = {};
        files.forEach(f => arquivos[f.caminho] = f.conteudo);

        try {
            const pastasRes = await req(`/studio/projetos/${currentProjectId}/pastas`);
            pastas = await pastasRes.json();
        } catch(e) {
            pastas = [];
        }

        if (!arquivos[currentFilePath]) {
            currentFilePath = arquivos['index.html'] ? 'index.html' : Object.keys(arquivos)[0] || 'index.html';
        }

        codeEditor.value = arquivos[currentFilePath] || '';
        
        updateHeader();
        renderFileTree();
        // 🔴 NÃO chama updatePreview aqui - só quando clicar no botão 🔴
        updateStatusBar();
    } catch(e) {
        console.error('Erro ao carregar arquivos:', e);
    }
}

async function saveFile(path, content) {
    await req(`/studio/projetos/${currentProjectId}/arquivos`, {
        method: 'POST',
        body: JSON.stringify({ caminho: path, conteudo: content })
    });
    arquivos[path] = content;
}

// 🔴 SALVAMENTO OTIMIZADO - sem preview automático 🔴
function saveCurrentFile() {
    if (!currentFilePath) return;
    const content = codeEditor.value;
    if (arquivos[currentFilePath] !== content) {
        arquivos[currentFilePath] = content;
        saveFile(currentFilePath, content);
        console.log('💾 Arquivo salvo');
    }
}

// ==================== HEADER ====================
function updateHeader() {
    const fileNameElem = document.getElementById('currentFileName');
    const fileMetaElem = document.getElementById('currentFileMeta');
    
    if (fileNameElem) fileNameElem.textContent = currentFilePath || 'Nenhum arquivo';
    
    if (fileMetaElem) {
        let tipo = 'Texto';
        if (currentFilePath.endsWith('.html')) tipo = 'HTML';
        else if (currentFilePath.endsWith('.css')) tipo = 'CSS';
        else if (currentFilePath.endsWith('.js')) tipo = 'JavaScript';
        else if (currentFilePath.endsWith('.py')) tipo = 'Python';
        fileMetaElem.textContent = 'Tipo: ' + tipo;
    }
}

// ==================== STATUS BAR ====================
function updateStatusBar() {
    const text = codeEditor.value;
    const cursorPos = codeEditor.selectionStart;
    const lines = text.substr(0, cursorPos).split('\n');
    const line = lines.length;
    const col = lines[lines.length - 1].length + 1;
    
    const statusBar = document.getElementById('statusBar');
    if (statusBar) {
        statusBar.innerHTML = `Ln ${line}, Col ${col}   UTF-8   `;
    }
}

// ==================== PREVIEW - APENAS MANUAL ====================
let currentHtmlFile = 'index.html';

function getHtmlFiles() {
    const htmlFiles = [];
    for (const path of Object.keys(arquivos)) {
        if (path.endsWith('.html')) {
            htmlFiles.push(path);
        }
    }
    return htmlFiles;
}

function setPreviewHtmlFile(filePath) {
    if (arquivos[filePath]) {
        currentHtmlFile = filePath;
        updatePreview();
        console.log('📄 Preview alterado para:', filePath);
    }
}

function createHtmlFileSelector() {
    const htmlFiles = getHtmlFiles();
    if (htmlFiles.length <= 1) return;
    
    let selector = document.getElementById('htmlFileSelector');
    if (!selector) {
        const previewHeader = document.querySelector('.preview-header');
        if (previewHeader) {
            selector = document.createElement('select');
            selector.id = 'htmlFileSelector';
            selector.style.marginLeft = '10px';
            selector.style.padding = '4px 8px';
            selector.style.fontSize = '11px';
            selector.style.background = '#3c3c3c';
            selector.style.color = 'white';
            selector.style.border = 'none';
            selector.style.borderRadius = '4px';
            selector.onchange = (e) => setPreviewHtmlFile(e.target.value);
            previewHeader.appendChild(selector);
        }
    }
    
    if (selector) {
        selector.innerHTML = '';
        htmlFiles.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            option.textContent = '📄 ' + file;
            if (file === currentHtmlFile) option.selected = true;
            selector.appendChild(option);
        });
    }
}

// 🔴 FUNÇÃO PREVIEW - SÓ É CHAMADA MANUALMENTE 🔴
function updatePreview() {
    console.log('🔄 Atualizando preview...');
    
    // Salvar conteúdo atual antes de atualizar o preview
    saveCurrentFile();
    
    // Obter o HTML do arquivo selecionado
    let htmlContent = arquivos[currentHtmlFile] || '';
    
    if (!htmlContent) {
        if (arquivos['index.html']) {
            currentHtmlFile = 'index.html';
            htmlContent = arquivos['index.html'];
        } else {
            for (const [path, content] of Object.entries(arquivos)) {
                if (path.endsWith('.html')) {
                    currentHtmlFile = path;
                    htmlContent = content;
                    break;
                }
            }
        }
    }
    
    if (!htmlContent) {
        htmlContent = '<h1>Sem conteúdo HTML</h1><p>Nenhum arquivo .html encontrado.</p>';
    }
    
    // Procurar CSS
    let cssContent = '';
    for (const [path, content] of Object.entries(arquivos)) {
        if (path.endsWith('.css')) {
            cssContent = content;
            break;
        }
    }
    
    // Procurar JavaScript
    let jsContent = '';
    for (const [path, content] of Object.entries(arquivos)) {
        if (path.endsWith('.js')) {
            jsContent = content;
            break;
        }
    }
    
    const safeJs = jsContent.replace(/<\/script/gi, '<\\/script');
    
    let doc = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>' + cssContent + '</style></head><body>' + htmlContent + '<script>' + safeJs + '<\/script></body></html>';
    
    if (preview) {
        preview.srcdoc = doc;
        console.log('✅ Preview atualizado - Arquivo:', currentHtmlFile);
    }
    
    createHtmlFileSelector();
}

// ==================== RENDER FILE TREE ====================
function renderFileTree() {
    if (!fileTree) return;
    fileTree.innerHTML = '';
    
    const filesInFolders = {};
    const rootFiles = [];
    
    Object.keys(arquivos).forEach(path => {
        if (path.includes('/')) {
            const folder = path.split('/')[0];
            if (!filesInFolders[folder]) filesInFolders[folder] = [];
            filesInFolders[folder].push(path);
        } else {
            rootFiles.push(path);
        }
    });
    
    const allFolders = [...new Set([...Object.keys(filesInFolders), ...pastas.map(p => p.nome)])].sort();
    
    allFolders.forEach(folder => {
        const folderDiv = document.createElement('div');
        folderDiv.className = 'tree-item tree-folder';
        folderDiv.innerHTML = '<div class="tree-row"><div class="tree-label" onclick="toggleFolder(\'' + folder + '\')">📁 ' + folder + '</div><div class="tree-actions"><button class="mini-btn" onclick="createFileInFolder(\'' + folder + '\')">+</button><button class="mini-btn mini-danger" onclick="deleteFolder(\'' + folder + '\')">×</button></div></div><div class="folder-files" id="folder-' + folder + '"></div>';
        
        const container = folderDiv.querySelector('.folder-files');
        const folderFiles = filesInFolders[folder] || [];
        
        folderFiles.sort().forEach(path => {
            const name = path.split('/').pop();
            const fileDiv = document.createElement('div');
            fileDiv.className = 'tree-item tree-file' + (currentFilePath === path ? ' active' : '');
            fileDiv.innerHTML = '<div class="tree-row"><div class="tree-label" onclick="openFile(\'' + path + '\')">📄 ' + name + '</div><div class="tree-actions"><button class="mini-btn mini-warning" onclick="renameFile(\'' + path + '\')">✏️</button><button class="mini-btn mini-danger" onclick="deleteFile(\'' + path + '\')">×</button></div></div>';
            container.appendChild(fileDiv);
        });
        
        fileTree.appendChild(folderDiv);
    });
    
    rootFiles.sort().forEach(path => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'tree-item tree-file' + (currentFilePath === path ? ' active' : '');
        fileDiv.innerHTML = '<div class="tree-row"><div class="tree-label" onclick="openFile(\'' + path + '\')">📄 ' + path + '</div><div class="tree-actions"><button class="mini-btn mini-warning" onclick="renameFile(\'' + path + '\')">✏️</button><button class="mini-btn mini-danger" onclick="deleteFile(\'' + path + '\')">×</button></div></div>';
        fileTree.appendChild(fileDiv);
    });
}

// ==================== FUNÇÕES GLOBAIS ====================
window.openFile = function(path) {
    if (arquivos[path]) {
        saveCurrentFile(); // Salvar antes de trocar de arquivo
        currentFilePath = path;
        codeEditor.value = arquivos[path];
        updateHeader();
        renderFileTree();
        updateStatusBar();
    } else {
        alert('Arquivo não encontrado: ' + path);
    }
};

window.toggleFolder = function(folder) {
    const el = document.getElementById('folder-' + folder);
    if (el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
};

window.deleteFile = async function(path) {
    if (confirm('Excluir ' + path + '?')) {
        await req('/studio/projetos/' + currentProjectId + '/arquivos/' + encodeURIComponent(path), { method: 'DELETE' });
        delete arquivos[path];
        if (currentFilePath === path) currentFilePath = 'index.html';
        await loadFiles();
    }
};

window.renameFile = async function(path) {
    const newName = prompt('Novo nome:', path.split('/').pop());
    if (newName && newName !== path.split('/').pop()) {
        const parts = path.split('/');
        parts.pop();
        const newPath = parts.length ? parts.join('/') + '/' + newName : newName;
        const content = arquivos[path];
        await saveFile(newPath, content);
        await req('/studio/projetos/' + currentProjectId + '/arquivos/' + encodeURIComponent(path), { method: 'DELETE' });
        delete arquivos[path];
        if (currentFilePath === path) currentFilePath = newPath;
        await loadFiles();
    }
};

window.createFileInFolder = async function(folder) {
    const name = prompt('Nome do arquivo (ex: novo.html):');
    if (name && name.includes('.')) {
        const path = folder + '/' + name;
        if (arquivos[path]) { alert('Já existe!'); return; }
        await saveFile(path, '');
        await loadFiles();
        openFile(path);
    } else if (name) {
        alert('Precisa de extensão!');
    }
};

window.deleteFolder = async function(folder) {
    const filesInFolder = Object.keys(arquivos).filter(f => f.startsWith(folder + '/'));
    if (filesInFolder.length > 0) {
        alert('Pasta não vazia! Exclua os arquivos primeiro.');
        return;
    }
    if (confirm('Excluir pasta ' + folder + '?')) {
        await req('/studio/projetos/' + currentProjectId + '/pastas', { method: 'DELETE', body: JSON.stringify({ nome: folder }) });
        await loadFiles();
    }
};

// ==================== AÇÕES PRINCIPAIS ====================
async function createNewFile() {
    const name = prompt('Nome do arquivo (ex: novo.html, style.css, script.js):');
    if (name && name.includes('.')) {
        if (arquivos[name]) { alert('Já existe!'); return; }
        
        let conteudo = '';
        const ext = name.split('.').pop().toLowerCase();
        if (ext === 'html') conteudo = '<h1>Novo arquivo HTML</h1>';
        else if (ext === 'css') conteudo = '/* Novo arquivo CSS */';
        else if (ext === 'js') conteudo = 'console.log("Novo arquivo JS");';
        else if (ext === 'py') conteudo = 'print("Olá Python!")';
        
        await saveFile(name, conteudo);
        await loadFiles();
        openFile(name);
    } else if (name) {
        alert('O arquivo precisa ter uma extensão (.html, .css, .js, .py)');
    }
}

async function createNewFolder() {
    const name = prompt('Nome da pasta:');
    if (name && name.trim()) {
        if (pastas.some(p => p.nome === name)) { alert('Já existe!'); return; }
        await req('/studio/projetos/' + currentProjectId + '/pastas', { method: 'POST', body: JSON.stringify({ nome: name.trim() }) });
        await loadFiles();
    }
}

async function createNewProject() {
    const name = prompt('Nome do novo projeto:');
    if (name && name.trim()) {
        await createProject(name.trim());
        await loadProjects();
        alert('Projeto "' + name + '" criado com sucesso!');
    }
}

async function renameCurrentProject() {
    const newName = prompt('Novo nome do projeto:', currentProjectName);
    if (newName && newName !== currentProjectName) {
        await req('/studio/projetos/' + currentProjectId, { method: 'PUT', body: JSON.stringify({ nome: newName }) });
        await loadProjects();
    }
}

async function deleteCurrentProject() {
    if (confirm('Tem certeza que deseja excluir o projeto "' + currentProjectName + '" permanentemente?')) {
        await req('/studio/projetos/' + currentProjectId, { method: 'DELETE' });
        await loadProjects();
    }
}

async function resetCurrentProject() {
    if (confirm('Resetar projeto? Todas as alterações serão perdidas!')) {
        const defaults = {
            'index.html': '<h1>Projeto Resetado</h1><p>Seu projeto foi resetado!</p>',
            'style.css': 'body { font-family: Arial; text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; }',
            'script.js': 'console.log("Projeto resetado!");'
        };
        for (const [path, content] of Object.entries(defaults)) {
            await saveFile(path, content);
        }
        await loadFiles();
    }
}

function copyCode() {
    navigator.clipboard.writeText(codeEditor.value);
    alert('Código copiado!');
}

function clearCurrentFile() {
    if (confirm('Limpar o arquivo atual?')) {
        codeEditor.value = '';
        saveCurrentFile();
    }
}

function run() {
    console.log('▶ Botão Executar clicado!');
    updatePreview();
}

function openMainFiles() {
    if (arquivos['index.html']) openFile('index.html');
    else alert('index.html não encontrado!');
}

// ==================== TERMINAL ====================
function openTerminal() {
    if (!currentFilePath.endsWith('.py')) {
        alert('Abra um arquivo .py primeiro!');
        return;
    }
    const terminalPanel = document.getElementById('terminalPanel');
    if (terminalPanel) terminalPanel.classList.add('active');
}

function runPython() {
    if (!currentFilePath.endsWith('.py')) {
        alert('Abra um arquivo .py primeiro!');
        return;
    }
    
    const terminalOutput = document.getElementById('terminalOutput');
    if (!terminalOutput) return;
    
    terminalOutput.innerHTML += '<div class="terminal-line terminal-info">>>> Executando ' + currentFilePath + '...</div>';
    
    const code = codeEditor.value;
    const lines = code.split('\n');
    let hasOutput = false;
    
    for (let line of lines) {
        const match = line.trim().match(/^print\s*\((.*)\)\s*$/);
        if (match) {
            hasOutput = true;
            let text = match[1].trim();
            if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) {
                text = text.slice(1, -1);
            }
            terminalOutput.innerHTML += '<div class="terminal-line terminal-success">' + text + '</div>';
        }
    }
    
    if (!hasOutput) {
        terminalOutput.innerHTML += '<div class="terminal-line terminal-info">✅ Programa executado (sem saída visível)</div>';
    }
    
    terminalOutput.innerHTML += '<div class="terminal-line terminal-info">>>> Finalizado</div>';
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function clearTerminal() {
    const terminalOutput = document.getElementById('terminalOutput');
    if (terminalOutput) terminalOutput.innerHTML = '<div class="terminal-line terminal-info">🧹 Terminal limpo</div>';
}

function closeTerminal() {
    const terminalPanel = document.getElementById('terminalPanel');
    if (terminalPanel) terminalPanel.classList.remove('active');
}

// ==================== MODAL ====================
function openModal() {
    const modal = document.getElementById('userModal');
    const overlay = document.getElementById('modalOverlay');
    if (modal) modal.classList.add('show');
    if (overlay) overlay.classList.add('show');
}

function closeModal() {
    const modal = document.getElementById('userModal');
    const overlay = document.getElementById('modalOverlay');
    if (modal) modal.classList.remove('show');
    if (overlay) overlay.classList.remove('show');
}

// ==================== DEBUG ====================
window.debugState = function() {
    console.log('=== DEBUG ===');
    console.log('Projeto:', currentProjectName, '(ID:', currentProjectId + ')');
    console.log('Arquivo atual:', currentFilePath);
    console.log('Arquivos:', Object.keys(arquivos));
    alert('📊 Projeto: ' + currentProjectName + '\nArquivos: ' + Object.keys(arquivos).length + '\n\nVer console (F12) para mais detalhes');
};

// ==================== EDITOR SHORTCUTS ====================
codeEditor.addEventListener('keydown', function(e) {
    // Tab key para indentar
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = this.selectionStart;
        const end = this.selectionEnd;
        const value = this.value;
        
        if (start === end) {
            this.value = value.substring(0, start) + '    ' + value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        } else {
            const lines = value.substring(start, end).split('\n');
            const indented = lines.map(line => '    ' + line).join('\n');
            this.value = value.substring(0, start) + indented + value.substring(end);
            this.selectionStart = start;
            this.selectionEnd = start + indented.length;
        }
        updateStatusBar();
    }
    
    // Ctrl+S - Salvar (sem atualizar preview)
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveCurrentFile();
        alert('✅ Arquivo salvo!');
    }
    
    // Ctrl+R - Atualizar Preview
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        updatePreview();
        alert('🔄 Preview atualizado!');
    }
});

// Atualizar status bar
codeEditor.addEventListener('click', updateStatusBar);
codeEditor.addEventListener('keyup', updateStatusBar);
codeEditor.addEventListener('select', updateStatusBar);

// 🔴 IMPORTANTE: NÃO atualiza o preview enquanto digita 🔴
// Apenas salva de forma silenciosa
codeEditor.addEventListener('input', function() {
    // Salvar com debounce de 1 segundo
    if (saveTimeout) clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        saveCurrentFile();
    }, 1000);
});

// ==================== EVENTOS DOS BOTÕES ====================
document.getElementById('newProjectBtn')?.addEventListener('click', createNewProject);
document.getElementById('renameProjectBtn')?.addEventListener('click', renameCurrentProject);
document.getElementById('deleteProjectBtn')?.addEventListener('click', deleteCurrentProject);
document.getElementById('createFolderBtn')?.addEventListener('click', createNewFolder);
document.getElementById('createFileBtn')?.addEventListener('click', createNewFile);
document.getElementById('createFolderBtnSidebar')?.addEventListener('click', createNewFolder);
document.getElementById('createFileBtnSidebar')?.addEventListener('click', createNewFile);
document.getElementById('renameFileBtn')?.addEventListener('click', () => renameFile(currentFilePath));
document.getElementById('deleteFileBtn')?.addEventListener('click', () => deleteFile(currentFilePath));

// 🔴 BOTÕES QUE ATUALIZAM O PREVIEW 🔴
document.getElementById('runBtn')?.addEventListener('click', () => {
    console.log('▶ Executando preview...');
    updatePreview();
});
document.getElementById('refreshPreviewBtn')?.addEventListener('click', () => {
    console.log('🔄 Atualizando preview...');
    updatePreview();
});

document.getElementById('openMainFilesBtn')?.addEventListener('click', openMainFiles);
document.getElementById('copyBtn')?.addEventListener('click', copyCode);
document.getElementById('clearBtn')?.addEventListener('click', clearCurrentFile);
document.getElementById('resetBtn')?.addEventListener('click', resetCurrentProject);
document.getElementById('openTerminalBtn')?.addEventListener('click', openTerminal);
document.getElementById('runPythonBtn')?.addEventListener('click', runPython);
document.getElementById('clearTerminalBtn')?.addEventListener('click', clearTerminal);
document.getElementById('closeTerminalBtn')?.addEventListener('click', closeTerminal);
document.getElementById('openUserModalBtn')?.addEventListener('click', openModal);
document.getElementById('closeModalBtn')?.addEventListener('click', closeModal);
document.getElementById('modalOverlay')?.addEventListener('click', closeModal);

document.getElementById('prevProjectBtn')?.addEventListener('click', async () => {
    const idx = projetos.findIndex(p => p.id === currentProjectId);
    const prev = projetos[idx <= 0 ? projetos.length - 1 : idx - 1];
    if (prev) await switchProject(prev.id);
});

document.getElementById('nextProjectBtn')?.addEventListener('click', async () => {
    const idx = projetos.findIndex(p => p.id === currentProjectId);
    const next = projetos[idx >= projetos.length - 1 ? 0 : idx + 1];
    if (next) await switchProject(next.id);
});

document.getElementById('projectSelector')?.addEventListener('change', (e) => {
    switchProject(e.target.value);
});

// ==================== INICIAR ====================
checkLogin();